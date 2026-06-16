import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect(r'D:\gitstore\wiz\My Knowledge\Data\18161262536\index.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# WIZ_DOCUMENT columns
c.execute('PRAGMA table_info(WIZ_DOCUMENT)')
cols = [r['name'] for r in c.fetchall()]
print('WIZ_DOCUMENT columns:')
for col in cols:
    print(' ', col)

# WIZ_DOCUMENT_ATTACHMENT table
c.execute("PRAGMA table_info(WIZ_DOCUMENT_ATTACHMENT)")
att_cols = [r['name'] for r in c.fetchall()]
print()
print('WIZ_DOCUMENT_ATTACHMENT columns:')
for col in att_cols:
    print(' ', col)

# How many unique docs have attachments?
c.execute('SELECT COUNT(DISTINCT DOCUMENT_GUID) FROM WIZ_DOCUMENT_ATTACHMENT')
print(f'\nDocs with attachments in local DB: {c.fetchone()[0]}')
c.execute("SELECT COUNT(*) FROM WIZ_DOCUMENT WHERE DOCUMENT_LOCATION LIKE '/%'")
print(f'Total real notes: {c.fetchone()[0]}')

# Check DOCUMENT_ATTACHMENT_COUNT column if exists
if 'DOCUMENT_ATTACHMENT_COUNT' in cols:
    c.execute('SELECT DOCUMENT_ATTACHMENT_COUNT, COUNT(*) cnt FROM WIZ_DOCUMENT GROUP BY DOCUMENT_ATTACHMENT_COUNT ORDER BY cnt DESC')
    print('\nATTACHMENT_COUNT distribution:')
    for row in c.fetchall():
        print(f'  count={row[0]}: {row[1]} notes')

conn.close()
