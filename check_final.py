import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('output/db/sync.db')
conn.row_factory = sqlite3.Row
total  = conn.execute('SELECT COUNT(*) FROM note_sync_rec').fetchone()[0]
synced = conn.execute('SELECT COUNT(*) FROM note_sync_rec WHERE sync_status=1').fetchone()[0]
neg1   = conn.execute('SELECT COUNT(*) FROM note_sync_rec WHERE sync_status=-1').fetchone()[0]
print('total=%d  synced=%d  failed=%d' % (total, synced, neg1))
rows = conn.execute('SELECT title, category, fail_reason FROM note_sync_rec WHERE sync_status=-1').fetchall()
print()
for r in rows:
    title = r['title']
    cat = r['category'].strip('/')
    reason = r['fail_reason'] or '(空)'
    print('  标题: %s' % title)
    print('  目录: %s' % cat)
    print('  原因: %s' % reason)
    print()
conn.close()
