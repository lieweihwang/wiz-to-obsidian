import os

wiz_dir = r"D:\gitstore\wiz\My Knowledge\Data\18161262536"
obs_dir = r"D:\gitstore\wiz2obsidian\output\note"

# Find all .ziw files
ziw_files = []
for root, dirs, files in os.walk(wiz_dir):
    for f in files:
        if f.endswith('.ziw'):
            ziw_files.append(os.path.relpath(os.path.join(root, f), wiz_dir))

# Find all .md files
md_files = []
for root, dirs, files in os.walk(obs_dir):
    for f in files:
        if f.endswith('.md'):
            md_files.append(os.path.relpath(os.path.join(root, f), obs_dir))

with open('compare_result_full.txt', 'w', encoding='utf-8') as f_out:
    f_out.write(f"WizNote 源目录 (.ziw) 文件数量: {len(ziw_files)}\n")
    f_out.write(f"Obsidian 输出目录 (.md) 文件数量: {len(md_files)}\n")

    wiz_dirs = {}
    for z in ziw_files:
        d = os.path.dirname(z).lower()
        wiz_dirs[d] = wiz_dirs.get(d, 0) + 1

    obs_dirs = {}
    for m in md_files:
        d = os.path.dirname(m).lower()
        obs_dirs[d] = obs_dirs.get(d, 0) + 1

    mismatches = []
    missing_in_obs = []

    for d, wiz_count in wiz_dirs.items():
        # 忽略 _attachments 目录下的 ziw（如果有的话），通常不在独立目录
        if '_attachments' in d:
            continue
        obs_count = obs_dirs.get(d, 0)
        if obs_count == 0:
            missing_in_obs.append((d, wiz_count))
        elif obs_count != wiz_count:
            mismatches.append((d, wiz_count, obs_count))

    f_out.write(f"\n源目录中存在，但输出目录中完全没有对应 .md 文件的目录数: {len(missing_in_obs)}\n")
    if missing_in_obs:
        f_out.write("示例:\n")
        for d, c in missing_in_obs[:20]:
            f_out.write(f"  - {d} (包含 {c} 个 .ziw)\n")

    f_out.write(f"\n.ziw 数量和 .md 数量不匹配的目录数: {len(mismatches)}\n")
    if mismatches:
        f_out.write("不匹配的目录:\n")
        mismatches.sort(key=lambda x: abs(x[1]-x[2]), reverse=True)
        for d, w_c, o_c in mismatches:
            f_out.write(f"  - {d}: Wiz有 {w_c} 个, Obs有 {o_c} 个\n")

