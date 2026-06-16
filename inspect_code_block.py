import sys, os, zipfile
sys.stdout.reconfigure(encoding='utf-8')

# 找一个含 transform 函数的笔记（C++ 主题）
wiz_dir = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\C++'
target = None
for root, dirs, files in os.walk(wiz_dir):
    for f in files:
        if f.endswith('.ziw'):
            path = os.path.join(root, f)
            try:
                with zipfile.ZipFile(path, 'r') as zf:
                    if 'index.html' in zf.namelist():
                        raw = zf.read('index.html')
                        # UTF-16 LE 解码
                        try:
                            html = raw.decode('utf-16-le', errors='replace')
                        except:
                            html = raw.decode('utf-8', errors='replace')
                        if 'transform' in html and 'InputIterator' in html:
                            target = (path, html)
                            break
            except:
                pass
    if target:
        break

if target:
    path, html = target
    print(f'找到笔记: {os.path.basename(path)}')
    # 找代码块结构
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # 查看所有 pre 标签
    pres = soup.find_all('pre')
    print(f'<pre> 标签数: {len(pres)}')
    if pres:
        print('第一个 <pre> 内容（前500字符）:')
        print(str(pres[0])[:500])
    # 查看 wiz 代码块特征
    code_divs = soup.find_all(attrs={'class': lambda c: c and 'code' in c})
    print(f'\n包含 code class 的元素数: {len(code_divs)}')
    if code_divs:
        print('第一个 code div（前500字符）:')
        print(str(code_divs[0])[:500])
    # 查找 li 标签（WizNote 代码行号常用）
    lis = soup.find_all('li', class_=lambda c: c and ('L' in (c or '')))
    print(f'\n<li class=L...> 数: {len(lis)}')
    if lis:
        print(str(lis[0]))
else:
    print('未找到含 transform 的笔记，随机找一个有代码的笔记')
    # 找含代码块特征的笔记
    for root, dirs, files in os.walk(r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\C++\C++总结'):
        for f in files[:3]:
            if f.endswith('.ziw'):
                path = os.path.join(root, f)
                try:
                    with zipfile.ZipFile(path, 'r') as zf:
                        if 'index.html' in zf.namelist():
                            raw = zf.read('index.html')
                            html = raw.decode('utf-16-le', errors='replace')
                            soup = BeautifulSoup(html, 'html.parser')
                            pres = soup.find_all('pre')
                            print(f'笔记: {f}, pre 数: {len(pres)}')
                            if pres:
                                print(str(pres[0])[:300])
                except:
                    pass
