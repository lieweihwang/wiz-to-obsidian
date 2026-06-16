import sys, os, zipfile
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

# === Format 4: table-gutter (11 notes) ===
print("=" * 60)
print("FORMAT 4: table-gutter")
print("=" * 60)
path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\工作经验\技术文章\如何阅读一份源代码.ziw'
with zipfile.ZipFile(path, 'r') as zf:
    raw = zf.read('index.html')
    html = raw.decode('utf-16-le', errors='replace')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find tables with gutter td
    for table in soup.find_all('table'):
        gutter = table.find('td', class_='gutter')
        code_td = table.find('td', class_='code')
        if gutter and code_td:
            pre = code_td.find('pre')
            if pre:
                # Get line divs
                lines = pre.find_all('div', class_='line')
                print(f"Lines: {len(lines)}")
                print(f"First 3 lines text:")
                for i, line in enumerate(lines[:3]):
                    print(f"  {i}: {repr(line.get_text())}")
                print(f"PRE style: {pre.get('style', '')[:80]}")
                print()
            break

# === Format 5: pre with highlight div ===
print("=" * 60)
print("FORMAT 5: div.highlight > pre > code.language-xxx")
print("=" * 60)
path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\C++\C++总结\C++移动语义.ziw'
with zipfile.ZipFile(path, 'r') as zf:
    raw = zf.read('index.html')
    html = raw.decode('utf-16-le', errors='replace')
    soup = BeautifulSoup(html, 'html.parser')
    
    for div in soup.find_all('div', class_='highlight'):
        pre = div.find('pre')
        if pre:
            code = pre.find('code')
            lang = ''
            if code:
                for cls in (code.get('class') or []):
                    if cls.startswith('language-'):
                        lang = cls[len('language-'):]
                        break
            text = pre.get_text()
            print(f"Language: {lang}")
            print(f"Text length: {len(text)}")
            print(f"First 200 chars: {repr(text[:200])}")
            has_cr = '\r\n' in text
            print(f"Contains cr+lf: {has_cr}")
            print()
            break
