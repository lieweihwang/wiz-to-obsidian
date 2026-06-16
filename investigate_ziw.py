"""
调查 _Attachments 目录下到底有什么文件，以及 1980 条找不到的笔记标题与实际文件名的关系
"""
import os, sys, sqlite3
sys.stdout.reconfigure(encoding='utf-8')

wiz_path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536'

# 找 1980 条有问题的笔记，各取 3 个，逐一检查目录
conn = sqlite3.connect(r'D:\gitstore\wiz2obsidian\output\db\sync.db')
conn.row_factory = sqlite3.Row
rows = conn.execute(
    "SELECT title, category FROM note_sync_rec WHERE sync_status=-1 AND fail_reason LIKE '%ziw%' LIMIT 20"
).fetchall()
conn.close()

print('找不到 .ziw 的笔记，检查实际目录内容:')
for r in rows[:10]:
    title    = r['title']
    category = r['category']
    rel = category.strip('/').replace('/', os.sep)
    note_dir = os.path.join(wiz_path, rel)
    print(f'\n标题: {title}')
    print(f'目录: {note_dir}')
    if os.path.isdir(note_dir):
        files = os.listdir(note_dir)
        ziw_files = [f for f in files if f.endswith('.ziw')]
        print(f'目录内 .ziw 文件: {ziw_files[:5]}')
    else:
        print('目录不存在!')
