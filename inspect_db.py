import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
db_path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\index.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# list tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print('Tables:', tables)

# look at WIZ_DOCUMENT table
cursor.execute("PRAGMA table_info(WIZ_DOCUMENT)")
cols = cursor.fetchall()
print('\nWIZ_DOCUMENT columns:')
for c in cols:
    print(' ', c)

# sample some rows
cursor.execute("SELECT DOCUMENT_GUID, DOCUMENT_TITLE, DOCUMENT_LOCATION, DOCUMENT_TYPE, DT_CREATED, DT_MODIFIED FROM WIZ_DOCUMENT LIMIT 5")
rows = cursor.fetchall()
print('\nSample rows:')
for r in rows:
    print(' ', r)

conn.close()
