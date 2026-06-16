import sys, os, zipfile
sys.stdout.reconfigure(encoding='utf-8')

wiz_dir = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\C++'
for root, dirs, files in os.walk(wiz_dir):
    for f in files:
        if f.endswith('.ziw'):
            path = os.path.join(root, f)
            try:
                with zipfile.ZipFile(path, 'r') as zf:
                    if 'index.html' in zf.namelist():
                        raw = zf.read('index.html')
                        html = raw.decode('utf-16-le', errors='replace')
                        if 'transform' in html and 'InputIterator' in html:
                            print(f'测试笔记: {f}')
                            from sync.html_note_parser import HtmlNoteParser
                            parser = HtmlNoteParser()
                            result = parser.parse_content(html)

                            # 查找代码块
                            in_code = False
                            block_count = 0
                            code_lines = []
                            for line in result.split('\n'):
                                if line.startswith('```') and not in_code:
                                    in_code = True
                                    code_lines = [line]
                                elif line.startswith('```') and in_code:
                                    in_code = False
                                    code_lines.append(line)
                                    block_count += 1
                                    if block_count <= 2:
                                        print(f'\n=== 代码块 {block_count} ===')
                                        print('\n'.join(code_lines[:12]))
                                        if len(code_lines) > 12:
                                            print(f'... (共 {len(code_lines)} 行) ...')
                                        print(code_lines[-1])
                                elif in_code:
                                    code_lines.append(line)

                            print(f'\n共找到 {block_count} 个代码块')
                            if block_count == 0:
                                # 检查是否还有旧格式
                                numbered = [l for l in result.split('\n') if l.strip() and l.strip()[0].isdigit() and '. ' in l[:5]]
                                print(f'旧格式行（数字. 开头）数: {len(numbered)}')
                                if numbered:
                                    print('示例:', numbered[:3])
                                # 检查 marker 是否在结果中
                                import re
                                markers = re.findall(r'WZCO\d+BLCK', result)
                                print(f'未替换的占位符: {markers}')
                            raise SystemExit
            except SystemExit:
                raise
            except Exception as e:
                import traceback
                traceback.print_exc()
