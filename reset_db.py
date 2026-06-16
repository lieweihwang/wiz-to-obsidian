import sqlite3
conn = sqlite3.connect('output/db/sync.db')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', [t[0] for t in tables])

for t in tables:
    name = t[0]
    if 'img' in name.lower() or 'image' in name.lower():
        cols = conn.execute(f'PRAGMA table_info({name})').fetchall()
        print(f'  {name} columns:', [c[1] for c in cols])
        count = conn.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0]
        print(f'  {name} count:', count)

# Reset notes
conn.execute('UPDATE note_sync_rec SET sync_status=0 WHERE sync_status=1')
conn.commit()
note_count = conn.execute('SELECT COUNT(*) FROM note_sync_rec WHERE sync_status=0').fetchone()[0]
print('Reset notes:', note_count)
conn.close()
