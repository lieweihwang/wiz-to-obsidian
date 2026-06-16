import zipfile, sys, re
sys.stdout.reconfigure(encoding='utf-8')

f = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\算法与数据结构\sungoshawk\10.栈和队列.ziw'
print('Opening:', f)

with zipfile.ZipFile(f, 'r') as z:
    raw = z.read('index.html')

print('BOM bytes:', raw[:4].hex())
print('Length:', len(raw))

if raw[:2] == b'\xff\xfe':
    html = raw.decode('utf-16-le', errors='replace')
    enc = 'utf-16-le'
elif raw[:2] == b'\xfe\xff':
    html = raw.decode('utf-16-be', errors='replace')
    enc = 'utf-16-be'
else:
    head = raw[:1024].decode('ascii', errors='replace')
    m = re.search(r'<meta[^>]+charset=["\']?([^"\'\s;>]+)', head, re.IGNORECASE)
    charset = m.group(1).lower() if m else None
    print('Detected charset:', charset)
    if charset in ('gb2312', 'gbk', 'gb18030'):
        html = raw.decode('gbk', errors='replace')
        enc = 'gbk'
    elif charset in ('utf-8', 'utf8'):
        html = raw.decode('utf-8', errors='replace')
        enc = 'utf-8'
    else:
        try:
            html = raw.decode('utf-8')
            enc = 'utf-8 (fallback)'
        except:
            html = raw.decode('gbk', errors='replace')
            enc = 'gbk (fallback)'

print('Decoded as:', enc)
print('\nFirst 800 chars:')
print(html[:800])
