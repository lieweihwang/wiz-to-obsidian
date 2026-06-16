from __future__ import annotations

from log import log
from sync.database import Database
from sync.file_manager import FileManager
from sync.image_handler import ImageHandler
from sync.local_wiz_reader import LocalWizReader
from sync.note_parser_factory import NoteParserFactory
from sync.note_property import NoteProperty
from sync.parsed_note import ParsedNote
from sync.wiz_link_resolver import WizLinkResolver


class LocalNoteSynchronizer:
    """
    本地模式同步器。
    从本地 .ziw 文件读取笔记内容，复用在线模式的所有解析器，不发起任何网络请求。
    """

    PAGE_SIZE = 200

    def __init__(self, reader: LocalWizReader, db: Database):
        self.reader = reader
        self.db = db
        # 初始化 wiz:// 链接解析器（共享 GUID→标题 缓存，避免重复查数据库）
        self.link_resolver = WizLinkResolver(reader.db_path)

    # ------------------------------------------------------------------
    # 主入口
    # ------------------------------------------------------------------

    def synchronize_notes(self):
        log.info('LocalNoteSynchronizer: 开始本地同步')

        # 1. 从本地 index.db 读取所有笔记，写入 sync.db（避免重复处理）
        all_notes = self.reader.get_all_notes()
        self._upsert_notes_to_db(all_notes)

        # 2. 分页处理未同步的笔记
        unsync_records = self.db.get_unsync_note_list(0, self.PAGE_SIZE)
        while unsync_records:
            self._sync_batch(unsync_records)
            max_id = max(r['id'] for r in unsync_records)
            log.info(f'已处理到 id={max_id}，继续获取下一批...')
            unsync_records = self.db.get_unsync_note_list(max_id, self.PAGE_SIZE)

        log.info('LocalNoteSynchronizer: 本地同步完成')

    # ------------------------------------------------------------------
    # 批量处理
    # ------------------------------------------------------------------

    def _upsert_notes_to_db(self, notes: list[dict]):
        """将笔记元信息写入 sync.db 的 note_sync_rec 表，跳过已存在的记录。"""
        pending = self.db.get_pending_sync_note_list(notes)
        if pending:
            log.info(f'新增 {len(pending)} 条待同步笔记')
            self.db.insert_note_list(pending)
        else:
            log.info('没有新增笔记需要写入 sync.db')

    def _sync_batch(self, records: list[dict]):
        for record in records:
            self._sync_single_note(record)

    # ------------------------------------------------------------------
    # 单条笔记处理
    # ------------------------------------------------------------------

    def _sync_single_note(self, record: dict):
        doc_guid = record['doc_guid']
        title = record['title']
        category = record['category']
        log.info(f'开始处理: guid={doc_guid} title={title}')

        try:
            # 读取 .ziw 内 index.html
            html = self.reader.get_note_html(doc_guid, title, category)

            # 确定笔记类型（可能需要根据 HTML 内容进行延迟检测）
            note_type = record['type']
            if note_type == '__auto__':
                note_type = self.reader.detect_type_from_html(html)
                log.info(f'自动检测类型: {note_type} guid={doc_guid}')

            # 协作笔记在本地没有完整离线内容，跳过
            if note_type == 'collaboration':
                log.warning(f'跳过协作笔记（本地无完整数据）: {title}')
                self.db.update_note_sync_status(
                    doc_guid, sync_status=False,
                    fail_reason='协作笔记在本地模式下无法转换（需要网络）'
                )
                return

            # 创建对应类型的解析器，解析 HTML → Markdown
            parser = NoteParserFactory.create_parser(note_type, title)
            parsed_note: ParsedNote = parser.process_content(html)

            # 处理图片：从 .ziw 直接提取，保存到 images/ 目录
            self._handle_images(record, parsed_note)

            # 处理附件：从 _Attachments 目录复制，追加到 Markdown
            self._handle_attachments(record, parsed_note)

            # 将 wiz:// 内部链接转换为 Obsidian [[]] 格式
            resolved_content = self.link_resolver.resolve(parsed_note.content)
            parsed_note.content = resolved_content

            # 拼接笔记属性（YAML front matter）
            note_prop = NoteProperty.from_sync_record(record).to_string()
            full_content = note_prop + parsed_note.content

            # 写入 Markdown 文件
            FileManager.save_md_to_file(category, title, full_content)

            # 更新同步状态为成功
            self.db.update_note_sync_status(doc_guid, sync_status=True, fail_reason='')
            log.info(f'处理完成: {title}')

        except FileNotFoundError as e:
            msg = f'找不到 .ziw 文件: {e}'
            log.warning(msg)
            self.db.update_note_sync_status(doc_guid, sync_status=False, fail_reason=msg)
        except Exception as e:
            log.exception(f'处理笔记异常: guid={doc_guid} title={title}')
            self.db.update_note_sync_status(doc_guid, sync_status=False, fail_reason=str(e))

    # ------------------------------------------------------------------
    # 图片处理
    # ------------------------------------------------------------------

    def _handle_images(self, record: dict, parsed_note: ParsedNote):
        """
        从 .ziw 内直接提取图片并保存到 output/note/<category>/images/ 目录，
        然后更新 parsed_note 中的图片链接。
        """
        if not parsed_note.need_upload_images:
            return

        doc_guid = record['doc_guid']
        title = record['title']
        category = record['category']

        # 从 .ziw 提取所有图片（key 为原始文件名，不含 Markdown 转义）
        ziw_images = self.reader.get_note_images(doc_guid, title, category)

        img_url_map = {}
        for img_name in parsed_note.need_upload_images:
            # img_name 已经是未转义的原始文件名（note_parser._extract_images 负责反转义）
            # 检查 db 中是否已处理过
            already_uploaded = self.db.get_uploaded_images(doc_guid, [img_name])
            if already_uploaded:
                log.info(f'图片已处理过，跳过: {img_name}')
                continue

            self.db.create_image_upload_record(doc_guid, img_name)

            if img_name in ziw_images:
                # 将图片字节保存到 images/ 目录
                FileManager.download_img_from_byte(record, img_name, ziw_images[img_name])
                try:
                    # 重命名为时间戳格式，并获取相对路径
                    uploaded_url = ImageHandler.handle(record, img_name)
                    img_url_map[img_name] = uploaded_url
                    self.db.update_img_sync_status(
                        doc_guid, img_name, sync_status=True, fail_reason='', upload_url=uploaded_url
                    )
                except Exception as e:
                    log.warning(f'图片重命名失败: {img_name}: {e}')
                    self.db.update_img_sync_status(
                        doc_guid, img_name, sync_status=False, fail_reason=str(e), upload_url=''
                    )
            else:
                msg = f'图片在 .ziw 中不存在: {img_name}'
                log.warning(msg)
                self.db.update_img_sync_status(
                    doc_guid, img_name, sync_status=False, fail_reason=msg, upload_url=''
                )

        # 替换笔记内容中的图片链接
        if img_url_map:
            parsed_note.replace_image_url(img_url_map)

    # ------------------------------------------------------------------
    # 附件处理
    # ------------------------------------------------------------------

    def _handle_attachments(self, record: dict, parsed_note: ParsedNote):
        """
        从本地 `{title}_Attachments/` 目录读取附件文件，
        复制到 output/note/{category}/attachments/ 目录，
        并在笔记末尾追加 `## 附件` 区块（与在线模式一致）。
        """
        title = record['title']
        category = record['category']

        # 读取本地附件文件 {fname: bytes}
        att_files = self.reader.get_note_attachment_files(title, category)
        if not att_files:
            return

        attachment_list = []
        safe_title = FileManager.sanitize_filename(title)
        for att_name, att_bytes in att_files.items():
            try:
                FileManager.download_attachment_from_byte(record, att_name, att_bytes)
                encoded_title = safe_title.replace(' ', '%20')
                encoded_att = att_name.replace(' ', '%20')
                relative_path = f'./{encoded_title}/{encoded_att}'
                attachment_list.append(f'- [{att_name}]({relative_path})')
                log.info(f'本地附件复制完成: {att_name}')
            except Exception as e:
                log.warning(f'本地附件复制失败: {att_name}: {e}')

        if attachment_list:
            attachment_section = '\n\n## 附件\n\n' + '\n'.join(attachment_list) + '\n'
            parsed_note.content += attachment_section
