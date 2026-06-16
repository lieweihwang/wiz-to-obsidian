import os, sys, sqlite3
sys.stdout.reconfigure(encoding='utf-8')

output_path = r'D:\gitstore\wiz2obsidian\output'
db_path = os.path.join(output_path, 'db', 'sync.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

total  = conn.execute('SELECT COUNT(*) FROM note_sync_rec').fetchone()[0]
synced = conn.execute('SELECT COUNT(*) FROM note_sync_rec WHERE sync_status=1').fetchone()[0]

# sync_status=0 且 fail_reason 不为空的（真正失败）
failed = conn.execute("SELECT COUNT(*) FROM note_sync_rec WHERE sync_status=0 AND fail_reason != ''").fetchone()[0]
# sync_status=0 且 fail_reason 为空的（从未被处理）
unprocessed = conn.execute("SELECT COUNT(*) FROM note_sync_rec WHERE sync_status=0 AND fail_reason = ''").fetchone()[0]

print(f'总计: {total}')
print(f'成功: {synced}')
print(f'失败(有原因): {failed}')
print(f'未处理(无原因): {unprocessed}')

# 失败原因统计
rows = conn.execute("""
    SELECT fail_reason, COUNT(*) cnt 
    FROM note_sync_rec 
    WHERE sync_status=0 AND fail_reason != '' 
    GROUP BY fail_reason 
    ORDER BY cnt DESC 
    LIMIT 10
""").fetchall()
if rows:
    print('\n失败原因 Top10:')
    for r in rows:
        print(f'  [{r["cnt"]:4d}次] {r["fail_reason"][:100]}')

# 未处理的样本
samples = conn.execute("""
    SELECT title, category, type 
    FROM note_sync_rec 
    WHERE sync_status=0 AND fail_reason = '' 
    LIMIT 10
""").fetchall()
if samples:
    print('\n未处理样本 (前10):')
    for s in samples:
        print(f'  [{s["type"]}] {s["category"]}{s["title"]}')

conn.close()
