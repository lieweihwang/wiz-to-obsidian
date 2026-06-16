from sync.note_parser import NoteParser
from sync.note_fixer import NoteFixer
import html2text
from bs4 import BeautifulSoup
import re


class HtmlNoteParser(NoteParser):

    @staticmethod
    def _fix_code_blocks(soup):
        """
        WizNote 有 5 种代码块格式，需要在 html2text 运行前全部提取出来，
        替换为占位符，运行后再还原为 Markdown 代码围栏。
        
        格式1: <pre class="prettyprint linenums"> + <ol>/<li> (Google Code Prettify)
        格式2: <div class="wiz-code-container"> + <textarea> (CodeMirror)
        格式3: <pre class="highlighter-hljs"> (hljs 剪藏)
        格式4: <table> 含 <td class="gutter"> + <td class="code"> (博客剪藏)
        格式5: <div class="highlight"> > <pre> > <code class="language-xxx"> (Hexo 等)
        """
        placeholders = []

        def _guess_lang(lang, text):
            """对缺失或错误标注的语言进行推断"""
            stripped = text.strip()
            # JSON 探测
            if not lang or lang.lower() in ('shell', 'javascript', 'js', 'text'):
                if (stripped.startswith('{') and stripped.endswith('}')) or \
                   (stripped.startswith('[') and stripped.endswith(']')):
                    return 'json'
            return lang

        def _clean(text):
            """统一清理 \\r，避免 Windows 写入时产生 \\r\\r\\n 双空行"""
            return text.replace('\r', '')

        def _make_placeholder(lang, code_text):
            lang = _guess_lang(lang, code_text)
            code_text = _clean(code_text)
            fence = f'```{lang}\n{code_text}\n```'
            marker = f'WZCO{len(placeholders)}BLCK'
            placeholders.append((marker, fence))
            return marker

        def _replace_with_marker(element, marker):
            div = soup.new_tag('div')
            div.string = marker
            element.replace_with(div)

        # ===== 格式1: Google Code Prettify =====
        for pre in soup.find_all('pre', class_=re.compile(r'\blinenums\b')):
            lang = ''
            first_code = pre.find('code', class_=re.compile(r'\blanguage-\w+\b'))
            if first_code:
                for cls in (first_code.get('class') or []):
                    if cls.startswith('language-'):
                        lang = cls[len('language-'):]
                        break
            lines = [li.get_text().rstrip() for li in pre.find_all('li')]
            marker = _make_placeholder(lang, '\n'.join(lines))
            _replace_with_marker(pre, marker)

        # ===== 格式2: CodeMirror (wiz-code-container) =====
        for container in soup.find_all('div', class_='wiz-code-container'):
            lang = container.get('data-mode', '').lower()
            textarea = container.find('textarea')
            if textarea:
                marker = _make_placeholder(lang, textarea.get_text())
                _replace_with_marker(container, marker)

        # ===== 格式3: highlighter-hljs =====
        for pre in soup.find_all('pre', class_='highlighter-hljs'):
            if pre.find('div', class_='wiz-code-container'):
                continue
            btn = pre.find('div', class_='esa-clipboard-button')
            if btn:
                btn.decompose()
            code_text = pre.get_text()
            if not code_text.strip():
                continue
            marker = _make_placeholder('', code_text)
            _replace_with_marker(pre, marker)

        # ===== 格式4: table 含 gutter + code td =====
        for table in soup.find_all('table'):
            gutter = table.find('td', class_='gutter')
            code_td = table.find('td', class_='code')
            if not (gutter and code_td):
                continue
            pre = code_td.find('pre')
            if not pre:
                continue
            # 代码行存放在 <div class="line"> 里
            line_divs = pre.find_all('div', class_='line')
            if line_divs:
                lines = [div.get_text().rstrip() for div in line_divs]
            else:
                lines = [pre.get_text()]
            marker = _make_placeholder('', '\n'.join(lines))
            _replace_with_marker(table, marker)

        # ===== 格式5: div.highlight > pre > code.language-xxx =====
        for div in soup.find_all('div', class_='highlight'):
            pre = div.find('pre')
            if not pre:
                continue
            code_tag = pre.find('code')
            lang = ''
            if code_tag:
                for cls in (code_tag.get('class') or []):
                    if cls.startswith('language-'):
                        lang = cls[len('language-'):]
                        break
            code_text = pre.get_text()
            if not code_text.strip():
                continue
            marker = _make_placeholder(lang, code_text)
            _replace_with_marker(div, marker)

        return soup, placeholders

    def parse_content(self, origin_content):
        soup = BeautifulSoup(origin_content, 'html.parser')

        # 预处理0: 清理 WizNote 编辑器残留
        # 0a. 移除 wiz-todo CSS <style> 块（219 篇笔记有此残留，会把 CSS 规则当文本输出）
        for style in soup.find_all('style', id='wiz_todo_style_id'):
            style.decompose()

        # 0b. 移除 <wiz-editor-doc> 自定义标签（保留子元素），
        #     防止 data-source 里的 base64 JSON 泄漏到输出中
        for wiz_tag in soup.find_all('wiz-editor-doc'):
            wiz_tag.unwrap()

        # 0c. 移除 wiz-todo 的占位图片（class 含 wiz-todo-img），
        #     这些是 checkbox 图标，会产生无效的 ![]() 引用
        for img in soup.find_all('img', class_=re.compile(r'wiz-todo')):
            img.decompose()

        # 预处理1: 修复 <img> 标签缺失或空的 src 属性
        for img in soup.find_all('img'):
            if not img.get('src'):
                img['src'] = ''

        # 预处理2: 简化新版 WizNote 编辑器的表格单元格
        # 新版编辑器在 <td> 里嵌套了 editor-container > editor-block > block-content > span
        # html2text 会把这些 div 当作块级元素插入换行，破坏表格结构
        for td in soup.find_all(['td', 'th']):
            # 移除 <br>，防止表格行被拆成多行
            for br in td.find_all('br'):
                br.decompose()
            # 检查是否是新版编辑器格式（含 editor-container）
            editor_div = td.find('div', class_='editor-container')
            if editor_div:
                # 提取纯文本，保留链接
                links = td.find_all('a')
                if links:
                    # 保留第一个链接
                    a = links[0]
                    link_html = str(a)
                    td.clear()
                    td.append(BeautifulSoup(link_html, 'html.parser'))
                else:
                    text = td.get_text().strip()
                    td.clear()
                    td.string = text

        # 预处理3: 把各种代码块替换成占位符
        soup, placeholders = HtmlNoteParser._fix_code_blocks(soup)

        cleaned_html = str(soup)

        # 配置 html2text
        h = html2text.HTML2Text()
        h.body_width = 0       # 禁止自动换行，防止表格/长行断裂
        h.pad_tables = True     # 表格列对齐
        markdown_content = h.handle(cleaned_html)

        # 把占位符替换回 Markdown 代码围栏
        for marker, fence in placeholders:
            markdown_content = markdown_content.replace(marker, fence)

        # 后置处理
        file_content = NoteFixer.fix(markdown_content)
        return file_content
