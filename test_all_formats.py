import sys, os, zipfile
from sync.html_note_parser import HtmlNoteParser
sys.stdout.reconfigure(encoding='utf-8')

parser = HtmlNoteParser()

test_cases = [
    ("C++ 移动语义 (div.highlight + code.language-cpp)",
     r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\C++\C++总结\C++移动语义.ziw',
     'MyClass'),
    ("Lua stack trace (table-gutter)", 
     r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\工作经验\技术文章\如何阅读一份源代码.ziw',
     'luaK_code'),
    ("RustDesk IP table",
     r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\生活经验\自建工具平台\搭建RustDesk远程控制平台.ziw',
     '43.142.122.129'),
]

for name, path, search_text in test_cases:
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    with zipfile.ZipFile(path, 'r') as zf:
        raw = zf.read('index.html')
        html = raw.decode('utf-16-le', errors='replace')
        result = parser.parse_content(html)
        
        # Find the area around the search text
        idx = result.find(search_text)
        if idx >= 0:
            start = max(0, idx - 200)
            end = min(len(result), idx + 500)
            print(result[start:end])
        else:
            print(f"'{search_text}' NOT FOUND in output!")
            print("First 500 chars:", result[:500])
