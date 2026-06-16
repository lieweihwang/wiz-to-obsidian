import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('output/db/sync.db')
conn.row_factory = sqlite3.Row

rows = conn.execute(
    'SELECT fail_reason, COUNT(*) cnt FROM note_sync_rec WHERE sync_status=-1 GROUP BY fail_reason ORDER BY cnt DESC LIMIT 10'
).fetchall()
print('sync_status=-1 的失败原因:')
for r in rows:
    reason = r['fail_reason'] or '(空)'
    print(f'  [{r["cnt"]:5d}] {reason[:100]}')

samples = conn.execute(
    'SELECT title, category, type, fail_reason FROM note_sync_rec WHERE sync_status=-1 LIMIT 10'
).fetchall()
print()
print('样本 (前10):')
for s in samples:
    reason = s['fail_reason'] or '(空)'
    print(f'  [{s["type"]}] {s["category"]}{s["title"]}')
    print(f'         fail={reason[:80]}')

conn.close()
