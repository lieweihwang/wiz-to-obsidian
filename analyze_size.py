import os, sys, sqlite3
sys.stdout.reconfigure(encoding='utf-8')

def dir_size_mb(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return total / 1024 / 1024

wiz_path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536'
src_size = dir_size_mb(wiz_path)

ziw_size = sum(os.path.getsize(os.path.join(r, f))
               for r, ds, fs in os.walk(wiz_path) for f in fs if f.endswith('.ziw')) / 1024 / 1024
att_size = sum(os.path.getsize(os.path.join(r, f))
               for r, ds, fs in os.walk(wiz_path) for f in fs if '_Attachments' in r) / 1024 / 1024
db_size  = os.path.getsize(os.path.join(wiz_path, 'index.db')) / 1024 / 1024

print('=== 原始数据 ===')
print(f'总大小:         {src_size:.1f} MB')
print(f'  .ziw 文件:    {ziw_size:.1f} MB')
print(f'  _Attachments: {att_size:.1f} MB')
print(f'  index.db:     {db_size:.1f} MB')

output_path = r'D:\gitstore\wiz2obsidian\output'
if os.path.exists(output_path):
    out_size = dir_size_mb(output_path)
    md_size  = sum(os.path.getsize(os.path.join(r, f))
                   for r, ds, fs in os.walk(output_path) for f in fs if f.endswith('.md')) / 1024 / 1024
    img_size = sum(os.path.getsize(os.path.join(r, f))
                   for r, ds, fs in os.walk(os.path.join(output_path, 'note')) for f in fs if 'images' in r) / 1024 / 1024
    oa_size  = sum(os.path.getsize(os.path.join(r, f))
                   for r, ds, fs in os.walk(os.path.join(output_path, 'note')) for f in fs if 'attachments' in r) / 1024 / 1024
    md_count = sum(1 for r, ds, fs in os.walk(output_path) for f in fs if f.endswith('.md'))
    print()
    print(f'=== 输出数据 ===')
    print(f'总大小:         {out_size:.1f} MB')
    print(f'  .md 文件:     {md_size:.1f} MB  ({md_count} 个)')
    print(f'  images/:      {img_size:.1f} MB')
    print(f'  attachments/: {oa_size:.1f} MB')
    print(f'比例:           {out_size/src_size*100:.1f}%')

db_path = os.path.join(output_path, 'db', 'sync.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    total  = conn.execute('SELECT COUNT(*) FROM note_sync_rec').fetchone()[0]
    synced = conn.execute('SELECT COUNT(*) FROM note_sync_rec WHERE sync_status=1').fetchone()[0]
    failed = conn.execute("SELECT COUNT(*) FROM note_sync_rec WHERE sync_status=0").fetchone()[0]
    rows   = conn.execute("SELECT fail_reason, COUNT(*) cnt FROM note_sync_rec WHERE sync_status=0 AND fail_reason != '' GROUP BY fail_reason ORDER BY cnt DESC LIMIT 5").fetchall()
    conn.close()
    print()
    print('=== 同步状态 ===')
    print(f'总计: {total}  成功: {synced}  未完成/失败: {failed}')
    if rows:
        print('失败原因 Top5:')
        for row in rows:
            print(f'  [{row[1]}次] {row[0][:100]}')
