import sys
sys.stdout.reconfigure(encoding='utf-8')
from sync.local_wiz_reader import LocalWizReader
reader = LocalWizReader(r'D:\gitstore\wiz\My Knowledge\Data\18161262536')

cases = [
    ('static_cast, dynamic_cast, reinterpret_cast, const_cast区别比较', '/My Notes/C++/C++总结/'),
    ('CentOS环境下，gdb调试中出现：Missing separate debuginfos, use_ debuginfo-install_____的问题', '/My Notes/调试方法/异常诊断与调试/'),
    ('菜鸟nginx源码剖析 配置与部署篇（一） 手把手实现nginx _quot_I love you_quot_', '/My Notes/nginx/菜鸟nginx源码剖析/'),
    ('Linux vi and vim editor: Tutorial and advanced features', '/My Notes/Linux/Linux工具/Vim/Vim使用/'),
    ('Linux下多线程查看工具(pstree、ps、pstack),linux命令之-pstree使用说明， linux 查看线程状态。 不指定', '/My Notes/调试方法/异常诊断与调试/'),
    ('Redis学习笔记~把redis放在DATA层，作为一种数据源，我认为更合理，也更符合我的面向对象原则', '/My Notes/数据库/Redis/教程/'),
    ('C++ #if #endif #define #ifdef #ifndef #if defined #if !defined详解', '/My Notes/C++/C++总结/'),
]
found = 0
for title, category in cases:
    import os
    path = reader._find_ziw('', title, category)
    ok = path is not None
    if ok:
        found += 1
    status = 'OK  ' if ok else 'FAIL'
    fname = os.path.basename(path) if path else '(not found)'
    print(f'{status}: {title[:55]}')
    if ok:
        print(f'      -> {fname}')

print(f'\n找到 {found}/{len(cases)}')
