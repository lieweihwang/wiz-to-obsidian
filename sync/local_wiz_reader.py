from __future__ import annotations
import os
import zipfile
import sqlite3
from datetime import datetime
from log import log


class LocalWizReader:
    """
    本地为知笔记数据读取器。
    从本地 index.db + .ziw 文件中读取笔记，替代 WizOpenApi 的网络调用。

    目录结构约定:
        <local_path>/
            index.db          -- SQLite，含 WIZ_DOCUMENT / WIZ_DOCUMENT_ATTACHMENT 等表
            My Notes/
                <分类>/
                    <子分类>/
                        <笔记标题>.ziw   -- ZIP 包，内含 index.html 和 index_files/
    """

    # .ziw 内 HTML 文件名
    ZIW_HTML_ENTRY = 'index.html'
    # .ziw 内图片资源目录前缀
    ZIW_IMG_PREFIX = 'index_files/'

    def __init__(self, local_path: str):
        """
        :param local_path: 为知笔记本地数据目录，例如:
                           D:\\gitstore\\wiz\\My Knowledge\\Data\\18161262536
        """
        self.local_path = local_path
        self.db_path = os.path.join(local_path, 'index.db')
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"找不到为知笔记数据库: {self.db_path}")

    # ------------------------------------------------------------------
    # 笔记列表
    # ------------------------------------------------------------------

    def get_all_notes(self) -> list[dict]:
        """
        读取本地 index.db，返回所有笔记记录列表。
        字段对齐在线模式的 note_sync_rec 结构（docGuid/title/category/type/created/accessed/url）。
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    DOCUMENT_GUID              AS docGuid,
                    DOCUMENT_TITLE             AS title,
                    DOCUMENT_LOCATION          AS category,
                    DOCUMENT_TYPE              AS type,
                    DOCUMENT_URL               AS url,
                    DT_CREATED                 AS dt_created,
                    DT_MODIFIED                AS dt_modified,
                    DOCUMENT_ATTACHEMENT_COUNT AS attachmentCount
                FROM WIZ_DOCUMENT
                ORDER BY DT_CREATED
            """)
            rows = cursor.fetchall()
        finally:
            conn.close()

        notes = []
        for row in rows:
            doc_guid = row['docGuid']
            title = row['title'] or 'untitled'
            category = row['category'] or ''
            url = row['url'] or ''

            # 跳过为知内部系统记录（category 不是以 "/" 开头的路径格式）
            if not category or not category.startswith('/'):
                log.info(f"跳过系统记录: guid={doc_guid} title={title} category={category}")
                continue

            # 时间：index.db 存储格式为 "YYYY-MM-DD HH:MM:SS"，转为毫秒时间戳
            created_ms = self._parse_dt_to_ms(row['dt_created'])
            modified_ms = self._parse_dt_to_ms(row['dt_modified'])

            # 自动检测笔记类型
            note_type = self._detect_note_type(doc_guid, title, row['type'])

            notes.append({
                'docGuid': doc_guid,
                'title': title,
                'category': category,
                'type': note_type,
                'url': url,
                'created': created_ms,
                'accessed': modified_ms,
                'version': created_ms,        # 用于兼容在线模式的分页逻辑
                'attachmentCount': row['attachmentCount'] or 0,  # 附件数，小写错字是 WizNote 原始 DB 的字段名
            })

        log.info(f"LocalWizReader: 共读取到 {len(notes)} 条有效笔记")
        return notes

    # ------------------------------------------------------------------
    # 笔记内容
    # ------------------------------------------------------------------

    def get_note_html(self, doc_guid: str, title: str, category: str) -> str:
        """
        定位并解压对应的 .ziw 文件，返回 index.html 文本内容。
        """
        ziw_path = self._find_ziw(doc_guid, title, category)
        if ziw_path is None:
            raise FileNotFoundError(f"找不到笔记 .ziw 文件: guid={doc_guid}, title={title}")

        with zipfile.ZipFile(ziw_path, 'r') as zf:
            if self.ZIW_HTML_ENTRY not in zf.namelist():
                raise ValueError(f".ziw 文件内没有 {self.ZIW_HTML_ENTRY}: {ziw_path}")
            raw = zf.read(self.ZIW_HTML_ENTRY)

        # 自动检测编码：优先 UTF-16 LE BOM，其次 UTF-8，再回退到 gbk
        html = self._decode_html(raw)
        return html

    # ------------------------------------------------------------------
    # 图片
    # ------------------------------------------------------------------

    def get_note_images(self, doc_guid: str, title: str, category: str) -> dict[str, bytes]:
        """
        从 .ziw 内 index_files/ 提取所有图片，返回 {文件名: 二进制内容} 字典。
        """
        ziw_path = self._find_ziw(doc_guid, title, category)
        if ziw_path is None:
            log.warning(f"get_note_images: 找不到 .ziw 文件 guid={doc_guid}")
            return {}

        images = {}
        with zipfile.ZipFile(ziw_path, 'r') as zf:
            for name in zf.namelist():
                if name.startswith(self.ZIW_IMG_PREFIX) and not name.endswith('/'):
                    img_name = name[len(self.ZIW_IMG_PREFIX):]
                    if img_name:
                        images[img_name] = zf.read(name)

        log.info(f"get_note_images: 找到 {len(images)} 张图片 guid={doc_guid}")
        return images

    # ------------------------------------------------------------------
    # 附件（来自 index.db WIZ_DOCUMENT_ATTACHMENT + .ziw 内文件）
    # ------------------------------------------------------------------

    def get_note_attachments(self, doc_guid: str) -> list[dict]:
        """
        从 index.db 读取附件列表，返回 [{'name': ..., 'attGuid': ...}, ...]
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ATTACHMENT_GUID AS attGuid,
                       ATTACHMENT_NAME AS name
                FROM WIZ_DOCUMENT_ATTACHMENT
                WHERE DOCUMENT_GUID = ?
            """, (doc_guid,))
            rows = cursor.fetchall()
        except Exception as e:
            log.warning(f"get_note_attachments 查询失败: {e}")
            return []
        finally:
            conn.close()

        return [{'attGuid': r['attGuid'], 'name': r['name']} for r in rows]

    def get_note_attachment_files(self, title: str, category: str) -> dict[str, bytes]:
        """
        从本地 `{title}_Attachments/` 目录读取所有附件文件。

        为知笔记本地附件存储规则：
          category = /My Notes/人工智能/AIGC/
          title    = 深入浅出Embedding：原理解析与应用实践.pdf
          附件目录 = <local_path>/My Notes/人工智能/AIGC/深入浅出Embedding：原理解析与应用实践.pdf_Attachments/

        :return: {文件名: 二进制内容} 字典；若无附件目录则返回 {}
        """
        att_dir = self._find_attachment_dir(title, category)
        if att_dir is None:
            return {}

        result = {}
        try:
            for fname in os.listdir(att_dir):
                fpath = os.path.join(att_dir, fname)
                if os.path.isfile(fpath):
                    with open(fpath, 'rb') as f:
                        result[fname] = f.read()
        except Exception as e:
            log.warning(f'get_note_attachment_files 读取失败: {att_dir}: {e}')

        log.info(f'get_note_attachment_files: 找到 {len(result)} 个附件 title={title}')
        return result

    def _find_attachment_dir(self, title: str, category: str) -> str | None:
        """
        定位附件目录 `{note_dir}/{title}_Attachments/`。
        WizNote 磁盘写入时特殊字符会被替换，使用模糊匹配兜底。
        """
        rel_dir = category.strip('/').replace('/', os.sep)
        note_dir = os.path.join(self.local_path, rel_dir)
        if not os.path.isdir(note_dir):
            return None

        # 精确匹配
        exact = os.path.join(note_dir, title + '_Attachments')
        if os.path.isdir(exact):
            return exact

        # 模糊匹配：遍历同级目录，找到以 _Attachments 结尾且与 title 匹配的
        suffix = '_Attachments'
        for entry in os.listdir(note_dir):
            if entry.endswith(suffix):
                folder_title = entry[:-len(suffix)]
                if self._fuzzy_match(folder_title, title):
                    log.warning(f'_find_attachment_dir: 模糊匹配 {entry!r} for title={title!r}')
                    return os.path.join(note_dir, entry)

        return None

    # ------------------------------------------------------------------
    # 内部辅助方法
    # ------------------------------------------------------------------

    def _find_ziw(self, doc_guid: str, title: str, category: str) -> str | None:
        """
        根据笔记的 category（目录）和 title（标题）定位 .ziw 文件路径。

        为知笔记本地目录结构：
          category = "/My Notes/C++/Boost/"
          title    = "Boost_bind使用"
          ziw_path = <local_path>/My Notes/C++/Boost/Boost_bind使用.ziw
        """
        # category 去掉开头 "/"，转为本地路径
        rel_dir = category.strip('/').replace('/', os.sep)
        note_dir = os.path.join(self.local_path, rel_dir)

        # 首选：精确匹配文件名
        ziw_path = os.path.join(note_dir, title + '.ziw')
        if os.path.exists(ziw_path):
            return ziw_path

        # 备选：目录存在时模糊匹配（标题中可能有特殊字符被替换）
        if os.path.isdir(note_dir):
            candidates = [f for f in os.listdir(note_dir) if f.endswith('.ziw')]

            # Pass 1: 精确去掉 .ziw 后比较
            for fname in candidates:
                if fname[:-4] == title:
                    return os.path.join(note_dir, fname)

            # Pass 2: 特殊字符替换的模糊匹配
            for fname in candidates:
                if self._fuzzy_match(fname[:-4], title):
                    log.warning(f"_find_ziw: 模糊匹配 '{fname}' for title='{title}'")
                    return os.path.join(note_dir, fname)

            # Pass 3: 标题含原始文件扩展名（如 .pdf/.vsdx）而 .ziw 去掉了扩展名时
            # 例如 title="c++ stack.pdf", 磁盘上是 "c++ stack.ziw"
            title_no_ext, ext = os.path.splitext(title)
            if ext:  # 标题确实有扩展名
                ziw_no_ext = os.path.join(note_dir, title_no_ext + '.ziw')
                if os.path.exists(ziw_no_ext):
                    log.warning(f"_find_ziw: 扩展名剥离匹配 '{title_no_ext}.ziw' for title='{title}'")
                    return ziw_no_ext
                # 再对去掉扩展名后的标题做模糊匹配
                for fname in candidates:
                    if self._fuzzy_match(fname[:-4], title_no_ext):
                        log.warning(f"_find_ziw: 扩展名剥离+模糊匹配 '{fname}' for title='{title}'")
                        return os.path.join(note_dir, fname)

        log.warning(f"_find_ziw: 找不到 .ziw: category={category} title={title} guid={doc_guid}")
        return None

    @staticmethod
    def _fuzzy_match(a: str, b: str) -> bool:
        """
        容错匹配：处理两类 WizNote 磁盘存储与 index.db 标题的差异：

        1. 字符替换：: / \\ * ? " < > | , ~ ( ) 等被替换为 -
           策略：将所有非字母数字汉字的字符统一去掉后比较。

        2. 文件名截断：标题过长时 WizNote 会在磁盘上截断文件名，
           例如标题 "static_cast, ..., const_cast区别比较" 被存为 "static_cast-...-const.ziw"。
           策略：若清理后的文件名是清理后标题的前缀（且长度 ≥ 10 字符），视为匹配。
        """
        import re
        # 只保留 Unicode 字母、数字、汉字，其余全部去掉
        clean = lambda s: re.sub(r'[^\w\u4e00-\u9fff]', '', s, flags=re.UNICODE).lower()
        ca, cb = clean(a), clean(b)
        # 精确匹配
        if ca == cb:
            return True
        # 前缀匹配（处理截断文件名）：短的是长的前缀，且足够长避免误匹配
        MIN_PREFIX = 10
        if len(ca) >= MIN_PREFIX and cb.startswith(ca):
            return True
        if len(cb) >= MIN_PREFIX and ca.startswith(cb):
            return True
        return False

    @staticmethod
    def _decode_html(raw: bytes) -> str:
        """
        自动检测 HTML 编码并解码。
        为知老版本笔记使用 UTF-16 LE（有 BOM \xff\xfe），新版本使用 UTF-8，
        更老的笔记使用 GB2312/GBK（meta charset 声明）。
        """
        # UTF-16 LE BOM
        if raw[:2] == b'\xff\xfe':
            return raw.decode('utf-16-le', errors='replace')
        # UTF-16 BE BOM
        if raw[:2] == b'\xfe\xff':
            return raw.decode('utf-16-be', errors='replace')

        # 先尝试 UTF-8 解码出 ASCII 可读的头部，从 <meta charset> 中提取声明编码
        try:
            head = raw[:1024].decode('ascii', errors='replace')
            charset = LocalWizReader._extract_charset(head)
            if charset:
                return raw.decode(charset, errors='replace')
        except Exception:
            pass

        # 尝试 UTF-8
        try:
            return raw.decode('utf-8')
        except UnicodeDecodeError:
            pass
        # 回退 GBK（旧版中文内容）
        try:
            return raw.decode('gbk', errors='replace')
        except Exception:
            return raw.decode('latin-1', errors='replace')

    @staticmethod
    def _extract_charset(head_text: str) -> str:
        """
        从 HTML 头部文本中提取 charset 声明。
        支持：
          <meta charset="utf-8">
          <meta http-equiv="Content-Type" content="text/html; charset=gb2312">
        返回小写 charset 字符串，或 None。
        """
        import re
        # <meta charset="...">
        m = re.search(r'<meta[^>]+charset=["\']?([^"\'\s;>]+)', head_text, re.IGNORECASE)
        if m:
            cs = m.group(1).strip().lower()
            # 标准化常见别名
            if cs in ('gb2312', 'gbk', 'gb18030'):
                return 'gbk'
            if cs in ('utf-8', 'utf8'):
                return 'utf-8'
            return cs
        return None

    def _detect_note_type(self, doc_guid: str, title: str, db_type: str | None) -> str:
        """
        自动检测笔记类型。
        优先使用 index.db 中的 DOCUMENT_TYPE，若为空则通过 index.html 内容特征判断。

        判断规则:
        1. db_type 非空 → 直接使用（'document' / 'lite/markdown' / 'collaboration' 等）
        2. db_type 为空 → 读取 .ziw 内 index.html：
           - 含 <meta name="wiz-data-type" content="collaboration"> → 'collaboration'
           - 标题以 .md 结尾 或 含 <pre class="wiz-code-mirror"...> → 'lite/markdown'
           - 其余 → 'document'（HTML 富文本）
        """
        if db_type and db_type.strip():
            return db_type.strip()

        # db_type 为空，需要自动检测
        # 先通过标题快速判断
        if title and title.strip().endswith('.md'):
            return 'lite/markdown'

        # 读取 .ziw 内容检测
        # 注意：此时还不知道 category，需要在 get_all_notes 中调用时传入
        # 这里作为延迟检测，返回一个标记，让 LocalNoteSynchronizer 在处理时再读取
        # 为了简化，此处返回 '__auto__' 作为延迟检测标记
        return '__auto__'

    def detect_type_from_html(self, html: str) -> str:
        """
        根据 index.html 内容特征判断笔记类型。
        由 LocalNoteSynchronizer 在已读取 HTML 内容后调用。
        """
        # 协作笔记特征：头部含特定 meta 标签
        if 'wiz-data-type' in html and 'collaboration' in html:
            return 'collaboration'
        # Lite/Markdown 笔记特征：wiz-code-mirror 是为知 Lite 编辑器的 CSS 类
        if 'wiz-code-mirror' in html or 'data-type="md"' in html:
            return 'lite/markdown'
        # 默认为 HTML 富文本笔记
        return 'document'

    @staticmethod
    def _parse_dt_to_ms(dt_str: str | None) -> int:
        """
        将 index.db 中的日期字符串（'YYYY-MM-DD HH:MM:SS'）转为毫秒时间戳。
        """
        if not dt_str:
            return 0
        try:
            dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            return int(dt.timestamp() * 1000)
        except Exception:
            return 0
