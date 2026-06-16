import sys
sys.stdout.reconfigure(encoding='utf-8')
from sync.local_wiz_reader import LocalWizReader
reader = LocalWizReader(r'D:\gitstore\wiz\My Knowledge\Data\18161262536')

cases = [
    ('atomic, spinlock and mutex性能比较', '/My Notes/C++/Boost/Boost总结/'),
    ('not1,not2,bind1st和bind2nd详解',    '/My Notes/C++/C++总结/'),
    ('所有者,群组,其他人',                 '/My Notes/Linux/Linux知识体系/'),
    ('linux sort,uniq,cut,wc命令详解',     '/My Notes/Linux/Linux知识体系/'),
    ('mysql ORDER BY,GROUP BY 和DISTINCT原理', '/My Notes/数据库/Mysql/Mysql知识体系/'),
    ('协议森林03 IP接力赛 (IP, ARP, RIP和BGP协议)', '/My Notes/网络/网络协议/'),
    ('MongoDB学习笔记~自己封装的Curd操作(查询集合对象属性,更新集合对象)', '/My Notes/数据库/MongoDB/总结/'),
]
found = 0
for title, category in cases:
    path = reader._find_ziw('', title, category)
    ok = path is not None
    if ok:
        found += 1
    status = 'OK  ' if ok else 'FAIL'
    import os
    fname = os.path.basename(path) if path else '(none)'
    print(f'  {status}: {title[:55]}')
    if ok:
        print(f'        -> {fname}')

print(f'找到 {found}/{len(cases)}')
