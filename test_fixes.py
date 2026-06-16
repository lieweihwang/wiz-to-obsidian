import sys, os, zipfile
from sync.html_note_parser import HtmlNoteParser
sys.stdout.reconfigure(encoding='utf-8')

parser = HtmlNoteParser()

# Test 1: wiz-todo CSS note
print('=== Test 1: wiz-todo CSS note ===')
path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\C++\C++总结\C++虚函数及虚函数表解析.ziw'
with zipfile.ZipFile(path, 'r') as zf:
    raw = zf.read('index.html')
    html = raw.decode('utf-16-le', errors='replace')
    result = parser.parse_content(html)
    # Check if wiz-todo CSS leaked
    if 'wiz-todo' in result.lower():
        print('FAIL: wiz-todo CSS still in output!')
        idx = result.lower().find('wiz-todo')
        print(result[max(0,idx-50):idx+200])
    else:
        print('OK: no wiz-todo CSS remnants')
    print(f'Output length: {len(result)} chars')
    print(f'First 200 chars: {result[:200]}')

# Test 2: wiz-editor-doc note
print('\n=== Test 2: wiz-editor-doc note (Roo Code) ===')
path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\人工智能\Agent智能体\搭建Roo Code编码助手.ziw'
with zipfile.ZipFile(path, 'r') as zf:
    raw = zf.read('index.html')
    html = raw.decode('utf-16-le', errors='replace')
    result = parser.parse_content(html)
    if 'eyJibG9j' in result:  # base64 prefix
        print('FAIL: base64 data leaked into output!')
    else:
        print('OK: no base64 data leak')
    # Check headings are correct
    for line in result.split('\n'):
        if line.startswith('#'):
            print(f'  {line}')

# Test 3: 无标题 check
print('\n=== Test 3: 无标题 placeholder ===')
from sync.note_fixer import fix_untitled_placeholder
test = '无标题\n\nThis is the content'
result = fix_untitled_placeholder(test)
print(f'Input:  {repr(test)}')
print(f'Output: {repr(result)}')

# Test 4: empty image ref
print('\n=== Test 4: empty image refs ===')
from sync.note_fixer import fix_empty_image_refs
test = 'before\n![]()\nafter\n![alt text]( )\nend'
result = fix_empty_image_refs(test)
print(f'Input:  {repr(test)}')
print(f'Output: {repr(result)}')
