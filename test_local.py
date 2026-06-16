"""
快速冒烟测试：只处理前 3 条笔记，验证本地转换流程是否正常。
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

from sync.init_dirs import init_output_dirs
from sync.database import Database
from sync.local_wiz_reader import LocalWizReader
from sync.local_note_synchronizer import LocalNoteSynchronizer

LOCAL_PATH = r'D:\gitstore\wiz\My Knowledge\Data\18161262536'

init_output_dirs()
reader = LocalWizReader(LOCAL_PATH)

# 只取前 3 条笔记做测试
all_notes = reader.get_all_notes()
test_notes = all_notes[:3]
print(f"\n将处理以下 {len(test_notes)} 条笔记：")
for n in test_notes:
    print(f"  [{n['type']}] {n['title']}  -> {n['category']}")

print()

with Database() as db:
    db.init()
    sync = LocalNoteSynchronizer(reader, db)
    sync._upsert_notes_to_db(test_notes)
    records = db.get_unsync_note_list(0, 10)
    print(f"sync.db 中待处理记录数: {len(records)}")
    sync._sync_batch(records)

print("\n=== 测试完成，检查 output/note/ 目录 ===")

# 列出生成的 md 文件
for root, dirs, files in os.walk('output/note'):
    for f in files:
        if f.endswith('.md'):
            fpath = os.path.join(root, f)
            size = os.path.getsize(fpath)
            print(f"  {fpath}  ({size} bytes)")
