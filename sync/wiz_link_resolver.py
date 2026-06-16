"""
WizNote 内部链接解析器。

将为知笔记内部链接（wiz://open_document?guid=...）转换为 Obsidian 内部链接（[[笔记标题]]）。

链接格式：
  wiz://open_document?guid=<doc_guid>&kbguid=&private_kbguid=<kb_guid>

转换结果：
  [显示文字](wiz://...) → [[目标笔记标题|显示文字]]
  自动降级：GUID 找不到时保留原始文字，去掉失效链接
"""
from __future__ import annotations

import re
import sqlite3
from urllib.parse import urlparse, parse_qs
from log import log


# 匹配 Markdown 行内链接中的完整 wiz:// URL
# 捕获组1: 显示文字, 捕获组2: 完整的 wiz://... URL
_WIZ_LINK_MD_PATTERN = re.compile(
    r'\[([^\]]*)\]\((wiz://open_document\?[^)]+)\)',
    re.IGNORECASE
)

# 匹配 HTML <a href="wiz://...">显示文字</a>（协作笔记或未经 html2text 处理的内容）
_WIZ_LINK_HTML_PATTERN = re.compile(
    r'<a[^>]+href=["\']?(wiz://open_document\?[^"\'> ]+)["\']?[^>]*>([^<]*)</a>',
    re.IGNORECASE
)


def _extract_guid_from_wiz_url(url: str) -> str | None:
    """
    从 wiz://open_document?guid=xxxx&kbguid=...&private_kbguid=... 中提取 guid。
    同时处理 &amp; 和 & 两种格式。
    """
    # 将 HTML 实体还原，统一使用 &
    url = url.replace('&amp;', '&')
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        guids = params.get('guid', [])
        return guids[0] if guids else None
    except Exception:
        # 回退：简单正则提取
        m = re.search(r'guid=([0-9a-f\-]{36})', url, re.IGNORECASE)
        return m.group(1) if m else None


class WizLinkResolver:
    """
    将 wiz:// 内部链接解析为 Obsidian [[笔记标题]] 格式。
    需要访问 index.db 以通过 GUID 查找笔记标题。
    """

    def __init__(self, db_path: str):
        """
        :param db_path: 为知笔记本地 index.db 文件路径
        """
        self.db_path = db_path
        self._cache: dict[str, str | None] = {}  # guid → title or None

    # 匹配括号内可能跨行的 wiz:// URL（html2text 会在 ~79 字符处换行）
    _WIZ_URL_WRAP_PATTERN = re.compile(
        r'(\(wiz://[^\)]*)\n([^\)]*\))',
        re.IGNORECASE
    )

    def resolve(self, markdown: str) -> str:
        """
        替换 markdown 中所有 wiz:// 内部链接为 Obsidian [[]] 格式。
        """
        # 第0步：合并 html2text 在 wiz:// URL 内部插入的换行符（重复直到没有换行）
        while True:
            new = self._WIZ_URL_WRAP_PATTERN.sub(lambda m: m.group(1) + m.group(2), markdown)
            if new == markdown:
                break
            markdown = new

        # 第1步：处理 HTML 残留链接（<a href="wiz://...">）
        markdown = _WIZ_LINK_HTML_PATTERN.sub(self._replace_html_link, markdown)
        # 第2步：处理 Markdown 格式链接 [显示](wiz://...)
        markdown = _WIZ_LINK_MD_PATTERN.sub(self._replace_md_link, markdown)
        return markdown

    def _replace_md_link(self, m: re.Match) -> str:
        display_text = m.group(1).strip()
        wiz_url = m.group(2).strip()
        guid = _extract_guid_from_wiz_url(wiz_url)
        if not guid:
            return display_text if display_text else m.group(0)
        return self._build_obsidian_link(guid, display_text)

    def _replace_html_link(self, m: re.Match) -> str:
        wiz_url = m.group(1).strip()
        display_text = m.group(2).strip()
        guid = _extract_guid_from_wiz_url(wiz_url)
        if not guid:
            return display_text if display_text else m.group(0)
        return self._build_obsidian_link(guid, display_text)

    def _build_obsidian_link(self, guid: str, display_text: str) -> str:
        """
        根据 GUID 查找目标笔记标题，构建 Obsidian 内部链接。

        结果规则：
        - 找到标题，且显示文字 == 标题：   [[标题]]
        - 找到标题，显示文字 != 标题：     [[标题|显示文字]]
        - 找不到标题（已删除笔记等）：      显示文字（保留文字，去掉链接）
        """
        title = self._lookup_title(guid)

        if title is None:
            # GUID 对应笔记不存在（可能已删除），降级为纯文本
            log.warning(f'WizLinkResolver: 找不到 GUID 对应笔记: {guid}, 保留显示文字: {display_text}')
            return display_text if display_text else f'[已删除笔记:{guid[:8]}]'

        # 文件系统保存时标题中的特殊字符会被替换为 _（参见 FileManager.sanitize_filename）
        safe_title = self._sanitize_for_obsidian(title)

        if display_text and display_text != title and display_text != safe_title:
            return f'[[{safe_title}|{display_text}]]'
        return f'[[{safe_title}]]'

    def _lookup_title(self, guid: str) -> str | None:
        """查询 index.db 获取 GUID 对应的笔记标题，带缓存。"""
        if guid in self._cache:
            return self._cache[guid]

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT DOCUMENT_TITLE FROM WIZ_DOCUMENT WHERE DOCUMENT_GUID = ?',
                (guid,)
            )
            row = cursor.fetchone()
            conn.close()
            title = row[0] if row else None
        except Exception as e:
            log.warning(f'WizLinkResolver: 查询数据库失败: {e}')
            title = None

        self._cache[guid] = title
        return title

    @staticmethod
    def _sanitize_for_obsidian(title: str) -> str:
        """
        将笔记标题转换为 Obsidian 链接中安全的形式。
        复用 FileManager.sanitize_filename 的逻辑（特殊字符 → _），
        同时去掉 .md 后缀（如果有）。
        """
        unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        safe = title
        for ch in unsafe_chars:
            safe = safe.replace(ch, '_')
        safe = safe.strip(' .')
        if safe.endswith('.md'):
            safe = safe[:-3]
        return safe
