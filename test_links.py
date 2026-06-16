"""
专项测试 wiz:// 内部链接转换
"""
import sys, os, shutil
sys.stdout.reconfigure(encoding='utf-8')

# ---- 先单独测试解析器逻辑 ----
from sync.wiz_link_resolver import WizLinkResolver

DB_PATH = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\index.db'
resolver = WizLinkResolver(DB_PATH)

# 用例1：已知真实 GUID
guid = 'f3db418e-a319-49b6-8316-33c9000ed74b'
title = resolver._lookup_title(guid)
print(f'GUID lookup: {guid} → {title!r}')

# 用例2：模拟完整 markdown 片段替换
sample_md = (
    '这是一篇测试笔记，参考 '
    '[C++ 11目录](wiz://open_document?guid=9aad132d-a3a9-4a1e-a16b-3ae3f66ae8a9'
    '&kbguid=&private_kbguid=6af99485-41a0-4bf0-8b58-1e3acd026995) 中的内容。\n\n'
    '另外参考 [这里](wiz://open_document?guid=00000000-0000-0000-0000-000000000000) 已删除的笔记。'
)
print('\n--- 输入 ---')
print(sample_md)
print('\n--- 转换后 ---')
print(resolver.resolve(sample_md))

# ---- 端到端测试：找一篇有 wiz:// 链接的笔记并转换 ----
print('\n\n=== 端到端测试 ===')
shutil.rmtree('output', ignore_errors=True)

from sync.init_dirs import init_output_dirs
from sync.database import Database
from sync.local_wiz_reader import LocalWizReader
from sync.local_note_synchronizer import LocalNoteSynchronizer

LOCAL_PATH = r'D:\gitstore\wiz\My Knowledge\Data\18161262536'
init_output_dirs()

reader = LocalWizReader(LOCAL_PATH)
# 找 C++ 11目录 笔记（已知有 wiz:// 链接）
all_notes = reader.get_all_notes()
target_notes = [n for n in all_notes if 'C++' in n['category'] and '目录' in n['title']][:2]
print(f'将处理 {len(target_notes)} 条含链接笔记:')
for n in target_notes:
    print(f'  {n["title"]}  [{n["category"]}]')

with Database() as db:
    db.init()
    sync = LocalNoteSynchronizer(reader, db)
    sync._upsert_notes_to_db(target_notes)
    records = db.get_unsync_note_list(0, 10)
    sync._sync_batch(records)

# 读取生成文件，查找 [[]] 链接
print('\n--- 生成的 Obsidian 链接 ---')
for root, dirs, files in os.walk('output/note'):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            content = open(path, encoding='utf-8').read()
            import re
            links = re.findall(r'\[\[.*?\]\]', content)
            if links:
                print(f'\n文件: {f}')
                for lk in links[:10]:
                    print(f'  {lk}')
