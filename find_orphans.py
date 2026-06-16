import os
import sqlite3

wiz_dir = r"D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes"
obs_dir = r"D:\gitstore\wiz2obsidian\output\note\My Notes"

# 找到所有的 .ziw 文件路径 (相对于 wiz_dir)
ziw_files = []
for root, dirs, files in os.walk(wiz_dir):
    for f in files:
        if f.endswith('.ziw'):
            ziw_files.append(os.path.relpath(os.path.join(root, f), wiz_dir).lower().replace('\\', '/'))

# 从数据库中获取所有的标题和分类
conn = sqlite3.connect('output/db/sync.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT title, category FROM note_sync_rec").fetchall()
conn.close()

db_expected_paths = []
for r in rows:
    cat = r['category'].lower().strip('/')
    if cat.startswith('my notes/'):
        cat = cat[9:]
    elif cat == 'my notes':
        cat = ''
    title = r['title'].lower()
    db_expected_paths.append((cat, title))

# 尝试匹配
unmatched_ziws = list(ziw_files)
for cat, title in db_expected_paths:
    # 模糊匹配找到对应的 ziw
    found = None
    for z in unmatched_ziws:
        if cat in z and (title[:10] in z or z.split('/')[-1].replace('.ziw', '') in title):
            found = z
            break
    if found:
        unmatched_ziws.remove(found)

with open('unmatched_ziws.txt', 'w', encoding='utf-8') as f:
    f.write(f"在本地磁盘上存在但似乎不在数据库同步记录中的 .ziw 数量: {len(unmatched_ziws)}\n")
    for z in unmatched_ziws[:50]:
        f.write(z + '\n')
