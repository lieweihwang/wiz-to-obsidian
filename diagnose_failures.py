import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from sync.local_wiz_reader import LocalWizReader
reader = LocalWizReader(r'D:\gitstore\wiz\My Knowledge\Data\18161262536')

# 测试几个有代表性的失败案例
cases = [
    ('README.md',           '/My Notes/架构和调优/QCon/QCon北京2018/'),
    ('README.md',           '/My Notes/架构和调优/顶尖互联网巨头技术架构/6.美团-点评技术架构/'),
    ('c++ stack.pdf',       '/My Notes/操作系统/内存管理/'),
    ('cmake教程.pdf',       '/My Notes/Linux/Linux工具/Make/书籍/'),
    ('SVN手册.pdf',         '/My Notes/版本控制/SVN总结/'),
    ('误删除libc.so.6 恢复', '/My Notes/Linux/Linux工具/常见问题集/'),
    ('Hacking ipcam like Harold in POI——攻击智能摄像头-洪宇',
     '/My Notes/架构和调优/QCon/QCon北京2016/打破规则，我是黑客专题/'),
]

wiz_path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536'

for title, category in cases:
    path = reader._find_ziw('', title, category)
    if path:
        print(f'OK   : {title}')
        print(f'       -> {os.path.basename(path)}')
    else:
        # 手动看目录里有什么
        rel = category.strip('/').replace('/', os.sep)
        note_dir = os.path.join(wiz_path, rel)
        exists = os.path.isdir(note_dir)
        if exists:
            files = [f for f in os.listdir(note_dir) if f.endswith('.ziw')]
            print(f'FAIL : {title}')
            print(f'       dir={note_dir}  ziw_files={files[:4]}')
        else:
            print(f'FAIL : {title}')
            print(f'       DIR NOT FOUND: {note_dir}')
