"""
测试本地附件处理：找一篇有 _Attachments 目录的笔记，验证附件被正确复制和追加到 Markdown
"""
import sys, shutil, os, re
sys.stdout.reconfigure(encoding='utf-8')
shutil.rmtree('output', ignore_errors=True)

from sync.init_dirs import init_output_dirs
from sync.database import Database
from sync.local_wiz_reader import LocalWizReader
from sync.local_note_synchronizer import LocalNoteSynchronizer

LOCAL_PATH = r'D:\gitstore\wiz\My Knowledge\Data\18161262536'
init_output_dirs()
reader = LocalWizReader(LOCAL_PATH)

# 测试 reader 能找到附件
print('=== 测试 get_note_attachment_files ===')
att_files = reader.get_note_attachment_files(
    '深入浅出Embedding：原理解析与应用实践.pdf',
    '/My Notes/人工智能/AIGC/'
)
print(f'找到附件: {list(att_files.keys())}')
for name, data in att_files.items():
    print(f'  {name}: {len(data)} bytes')

print()
att_files2 = reader.get_note_attachment_files(
    '玩转AIGC与应用部署.pdf',
    '/My Notes/人工智能/AIGC/'
)
print(f'找到附件: {list(att_files2.keys())}')

# 端到端转换两篇有附件的笔记
print('\n=== 端到端转换 ===')
all_notes = reader.get_all_notes()
targets = [n for n in all_notes if n['category'] == '/My Notes/人工智能/AIGC/']
print(f'将转换 {len(targets)} 篇笔记:')
for n in targets:
    print(f'  {n["title"]}')

with Database() as db:
    db.init()
    sync = LocalNoteSynchronizer(reader, db)
    sync._upsert_notes_to_db(targets)
    records = db.get_unsync_note_list(0, 20)
    sync._sync_batch(records)

# 检查结果
print('\n=== 检查输出 ===')
for root, dirs, files in os.walk('output'):
    for f in files:
        path = os.path.join(root, f)
        rel = os.path.relpath(path, 'output')
        size = os.path.getsize(path)
        if f.endswith('.md'):
            content = open(path, encoding='utf-8').read()
            att_section = '## 附件' in content
            att_links = re.findall(r'\[([^\]]+)\]\(./attachments/([^)]+)\)', content)
            print(f'[MD] {rel} | 有附件区块: {att_section} | 附件链接: {att_links}')
        elif 'attachments' in root:
            print(f'[ATT] {rel} | {size} bytes')
