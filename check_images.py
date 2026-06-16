import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

# Search in both output locations
for base_dir in [r'D:\gitstore\obsidian\note', r'D:\gitstore\wiz2obsidian\output\note']:
    print(f'\n=== Searching in {base_dir} ===')
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if 'V2ray' in f and f.endswith('.md'):
                md_path = os.path.join(root, f)
                print(f'Found: {md_path}')
                
                with open(md_path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                
                # Find all image references
                refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
                print(f'Image refs ({len(refs)}):')
                for alt, url in refs:
                    print(f'  ![{alt[:20]}]({url})')
                
                # Check parent dir for attachment folders
                note_dir = os.path.dirname(md_path)
                for item in os.listdir(note_dir):
                    full = os.path.join(note_dir, item)
                    if os.path.isdir(full) and 'V2ray' in item:
                        sub_files = os.listdir(full)
                        print(f'Attachment dir: {item}/ ({len(sub_files)} files)')
                        for sf in sub_files:
                            print(f'  {sf}')
                
                # Check image existence
                for alt, url in refs[:3]:
                    abs_path = os.path.normpath(os.path.join(note_dir, url))
                    exists = os.path.exists(abs_path)
                    print(f'Check: {url} -> {"OK" if exists else "MISSING"}')
