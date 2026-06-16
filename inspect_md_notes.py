import sys, os, zipfile
sys.stdout.reconfigure(encoding='utf-8')

from sync.local_wiz_reader import LocalWizReader
reader = LocalWizReader(r'D:\gitstore\wiz\My Knowledge\Data\18161262536')

# 检查几个失败的 .md 笔记内容
cases = [
    ('仇恨管理.md',          '/My Notes/工作经验/腾讯公司/XGame/设计文档/'),
    ('加密解密工具.md',       '/My Notes/信息安全/其他/'),
    ('README.md',            '/My Notes/架构和调优/QCon/QCon北京2018/'),
    ('README.md',            '/My Notes/架构和调优/QCon/QCon北京2019/'),
]

for title, category in cases:
    path = reader._find_ziw('', title, category)
    print(f'\n标题: {title}  分类: {category}')
    if not path:
        print('  _find_ziw 仍然找不到!')
        continue
    print(f'  找到: {os.path.basename(path)}')
    # 读取 .ziw 内容
    try:
        with zipfile.ZipFile(path, 'r') as zf:
            files = zf.namelist()
            print(f'  ZIP 内部文件: {files}')
            # 读第一个内容文件
            for fname in files:
                if fname.endswith(('.html', '.htm', '.md', '.txt')):
                    content = zf.read(fname)
                    print(f'  {fname} 前300字节: {content[:300]}')
                    break
    except Exception as e:
        print(f'  读取失败: {e}')
