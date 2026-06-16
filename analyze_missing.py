import os, sys, sqlite3
sys.stdout.reconfigure(encoding='utf-8')

# 检查本地 index.db 总记录数
wiz_db = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\index.db'
conn = sqlite3.connect(wiz_db)

total_docs = conn.execute('SELECT COUNT(*) FROM WIZ_DOCUMENT').fetchone()[0]
valid_docs = conn.execute("SELECT COUNT(*) FROM WIZ_DOCUMENT WHERE DOCUMENT_LOCATION LIKE '/%'").fetchone()[0]
skipped    = total_docs - valid_docs

print(f'WIZ_DOCUMENT 总行数: {total_docs}')
print(f'  有效笔记(/ 开头): {valid_docs}')
print(f'  系统记录(跳过):   {skipped}')

# 进一步按 DOCUMENT_TYPE 分布
rows = conn.execute("""
    SELECT DOCUMENT_TYPE, COUNT(*) cnt 
    FROM WIZ_DOCUMENT 
    WHERE DOCUMENT_LOCATION LIKE '/%' 
    GROUP BY DOCUMENT_TYPE 
    ORDER BY cnt DESC
""").fetchall()
print('\n有效笔记的类型分布:')
for r in rows:
    print(f'  {r[0] or "(空)":30s} {r[1]:5d}')

# 有效笔记中 .ziw 是否存在
wiz_notes_path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536'
rows2 = conn.execute("""
    SELECT DOCUMENT_GUID, DOCUMENT_TITLE, DOCUMENT_LOCATION 
    FROM WIZ_DOCUMENT 
    WHERE DOCUMENT_LOCATION LIKE '/%'
""").fetchall()

missing_ziw = 0
total_valid = 0
for r in rows2:
    total_valid += 1
    title = r[1] or 'untitled'
    category = r[2] or ''
    rel = category.strip('/').replace('/', os.sep)
    ziw = os.path.join(wiz_notes_path, rel, title + '.ziw')
    if not os.path.exists(ziw):
        # 尝试模糊匹配
        note_dir = os.path.join(wiz_notes_path, rel)
        if os.path.isdir(note_dir):
            found = any(f.endswith('.ziw') for f in os.listdir(note_dir))
            if not found:
                missing_ziw += 1
        else:
            missing_ziw += 1

print(f'\n有效笔记中找不到 .ziw 的: {missing_ziw} / {total_valid}')
conn.close()
