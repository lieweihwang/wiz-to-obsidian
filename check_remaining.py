import sqlite3, sys, os
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('output/db/sync.db')
conn.row_factory = sqlite3.Row
total  = conn.execute('SELECT COUNT(*) FROM note_sync_rec').fetchone()[0]
synced = conn.execute('SELECT COUNT(*) FROM note_sync_rec WHERE sync_status=1').fetchone()[0]
neg1   = conn.execute('SELECT COUNT(*) FROM note_sync_rec WHERE sync_status=-1').fetchone()[0]
print(f'总计: {total}  成功: {synced}  仍然失败: {neg1}')

# 失败的样本
rows = conn.execute('SELECT title, category FROM note_sync_rec WHERE sync_status=-1 LIMIT 30').fetchall()
print()
print('仍然失败的笔记样本:')
for r in rows:
    title    = r['title']
    category = r['category']
    print(f'  {category}{title}')

# 检查这些笔记的 category 目录里有什么 .ziw 文件
print()
print('对应目录实际文件:')
wiz_path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536'
for r in rows[:5]:
    title    = r['title']
    category = r['category']
    rel = category.strip('/').replace('/', os.sep)
    note_dir = os.path.join(wiz_path, rel)
    if os.path.isdir(note_dir):
        ziw_files = [f for f in os.listdir(note_dir) if f.endswith('.ziw')]
        # 找和 title 最相似的
        similar = [f for f in ziw_files if title[:4] in f or f[:4] in title]
        print(f'  title={title}')
        print(f'  similar={similar[:3]}')
    else:
        print(f'  目录不存在: {note_dir}')
conn.close()
