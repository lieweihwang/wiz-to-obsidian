from sync.note_parser import NoteParser
from bs4 import BeautifulSoup
from sync.note_fixer import NoteFixer


class LiteNoteParser(NoteParser):
    def parse_content(self, origin_content):
        # 尝试标准 lite/markdown 解析（内容在 <pre> 标签内）
        soup = BeautifulSoup(origin_content, 'html.parser')
        body_tag = soup.find('body')

        if body_tag is not None:
            first_pre_tag = body_tag.find('pre')
            if first_pre_tag is not None:
                # 标准格式：从 <pre> 取文本，再经 NoteFixer 处理
                markdown_content = first_pre_tag.get_text()
                return NoteFixer.fix(markdown_content)

        # 回退：部分 wiz-code-mirror 笔记没有 <pre>，内容在 div 中。
        # 使用 HtmlNoteParser 做完整的 HTML → Markdown 转换（避免二次 NoteFixer）
        from sync.html_note_parser import HtmlNoteParser
        return HtmlNoteParser().parse_content(origin_content)

    @staticmethod
    def parse(origin_content):
        """保留向后兼容的静态方法入口。"""
        soup = BeautifulSoup(origin_content, 'html.parser')
        body_tag = soup.find('body')
        if body_tag is None:
            return origin_content
        first_pre_tag = body_tag.find('pre')
        if first_pre_tag is None:
            return origin_content
        return first_pre_tag.get_text()
