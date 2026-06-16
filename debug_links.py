import zipfile, sys, re, html2text as h2t
sys.stdout.reconfigure(encoding='utf-8')
f = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\C++\C++11标准\C++ 11目录.ziw'
with zipfile.ZipFile(f, 'r') as z:
    raw = z.read('index.html')
html = raw.decode('utf-16-le', errors='replace')

md = h2t.html2text(html)

# Find wiz:// links in markdown, show raw content
pattern = r'\[[^\]]*\]\(wiz://[^)]*\)'
links = re.findall(pattern, md, re.DOTALL)
print(f'Found {len(links)} wiz links in markdown:')
for l in links[:8]:
    print(repr(l))
