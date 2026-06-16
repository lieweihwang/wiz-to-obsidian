import sqlite3, sys, os
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('output/db/sync.db')
conn.row_factory = sqlite3.Row
rows = conn.execute(
    "SELECT doc_guid, title, category FROM note_sync_rec WHERE sync_status=-1"
).fetchall()
conn.close()

print(f'剩余 {len(rows)} 条失败:')
wiz_path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536'

for r in rows:
    guid  = r['doc_guid']
    title = r['title']
    cat   = r['category']
    print(f'\n  GUID : {guid}')
    print(f'  标题 : {title}')
    print(f'  分类 : {cat}')

    # 在整个 wiz_path 下全局搜索这个 title 相关的 .ziw 文件
    found_global = []
    for root, dirs, files in os.walk(wiz_path):
        for f in files:
            if not f.endswith('.ziw'):
                continue
            stem = f[:-4]
            # 简单：stem 包含 title 前 8 个字符，或 title 包含 stem 前 8 个字符
            if title[:8] in stem or stem[:8] in title:
                found_global.append(os.path.join(root, f))
    if found_global:
        print(f'  全局搜索找到:')
        for p in found_global[:3]:
            print(f'    {p}')
    else:
        print(f'  全局搜索: 未找到任何相似 .ziw')
