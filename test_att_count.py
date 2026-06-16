import sys, shutil, sqlite3
sys.stdout.reconfigure(encoding='utf-8')
shutil.rmtree('output', ignore_errors=True)

from sync.init_dirs import init_output_dirs
from sync.database import Database
from sync.local_wiz_reader import LocalWizReader

LOCAL_PATH = r'D:\gitstore\wiz\My Knowledge\Data\18161262536'
init_output_dirs()
reader = LocalWizReader(LOCAL_PATH)

# 验证 attachmentCount 被正确读取
notes = reader.get_all_notes()
has_att = [n for n in notes if n.get('attachmentCount', 0) > 0]
no_att  = [n for n in notes if n.get('attachmentCount', 0) == 0]
print(f'总笔记: {len(notes)}')
print(f'有附件: {len(has_att)}  (attachmentCount > 0)')
print(f'无附件: {len(no_att)}  (attachmentCount = 0)')
print('有附件样例:')
for n in has_att[:3]:
    print(f'  {n["title"]}  attachmentCount={n["attachmentCount"]}')

# 写入 DB，验证 attachment_count 被持久化
with Database() as db:
    db.init()
    db.insert_note_list(notes[:10])
    conn = sqlite3.connect('output/db/sync.db')
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT title, attachment_count FROM note_sync_rec LIMIT 10').fetchall()
    print()
    print('DB 中的 attachment_count:')
    for r in rows:
        print(f'  attachment_count={r["attachment_count"]}  {r["title"]}')
    conn.close()
