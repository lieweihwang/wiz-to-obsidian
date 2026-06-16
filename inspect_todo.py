import sys, os, zipfile, re
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

# Find notes with actual wiz-todo checked/unchecked labels
wiz_dir = r'D:\gitstore\wiz\My Knowledge\Data\18161262536'
found = 0
for root, dirs, files in os.walk(wiz_dir):
    for f in files:
        if not f.endswith('.ziw'):
            continue
        path = os.path.join(root, f)
        try:
            with zipfile.ZipFile(path, 'r') as zf:
                raw = zf.read('index.html')
                html = raw.decode('utf-16-le', errors='replace')
                if 'wiz-todo-label-checked' in html or 'wiz-todo-label-unchecked' in html:
                    found += 1
                    if found <= 2:
                        print(f'FILE: {f}')
                        # Find the todo labels
                        soup = BeautifulSoup(html, 'html.parser')
                        for label in soup.find_all('label'):
                            cls = ' '.join(label.get('class', []))
                            if 'wiz-todo' in cls:
                                checked = 'checked' in cls
                                text = label.get_text().strip()[:50]
                                print(f'  [{"x" if checked else " "}] {text}')
                        # Show raw HTML of one todo item
                        idx = html.find('wiz-todo-label')
                        if idx >= 0:
                            print('\nRAW HTML SAMPLE:')
                            start = max(0, idx - 200)
                            print(html[start:start+500])
                        print('---')
        except:
            pass

print(f'\nTotal notes with todo items: {found}')
