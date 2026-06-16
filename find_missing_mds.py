import os
import sqlite3
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sync.file_manager import FileManager

obs_dir = r"D:\gitstore\wiz2obsidian\output\note\My Notes"

# Find all .md files
md_files = set()
for root, dirs, files in os.walk(obs_dir):
    for f in files:
        if f.endswith('.md'):
            rel_path = os.path.relpath(os.path.join(root, f), obs_dir).lower().replace('\\', '/')
            md_files.add(rel_path)

# Check database
conn = sqlite3.connect('output/db/sync.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT title, category FROM note_sync_rec WHERE sync_status=1").fetchall()
conn.close()

missing_mds = []
for r in rows:
    cat = r['category'].strip('/')
    if cat.startswith('My Notes/'):
        cat = cat[9:]
    elif cat == 'My Notes':
        cat = ''
    else:
        continue # Not in My Notes
        
    title = FileManager.sanitize_filename(r['title'])
    if title.lower().endswith('.md'):
        title = title[:-3]
    
    expected_path = f"{cat}/{title}.md".strip('/').lower()
    
    if expected_path not in md_files:
        missing_mds.append(expected_path)

with open('missing_mds3.txt', 'w', encoding='utf-8') as f:
    f.write(f"数据库记录为成功，但在输出目录找不到 .md 文件的数量: {len(missing_mds)}\n")
    for m in missing_mds:
        f.write(m + '\n')
