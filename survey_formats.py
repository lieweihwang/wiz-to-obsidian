import sys, os, zipfile
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes'
format_counts = {
    'linenums': 0,
    'wiz-code-container': 0,
    'highlighter-hljs': 0,
    'table-gutter': 0,
    'pre-highlight': 0,
}
sample_files = {k: [] for k in format_counts}

for root, dirs, files in os.walk(path):
    for f in files:
        if not f.endswith('.ziw'):
            continue
        fpath = os.path.join(root, f)
        try:
            with zipfile.ZipFile(fpath, 'r') as zf:
                if 'index.html' not in zf.namelist():
                    continue
                raw = zf.read('index.html')
                try:
                    html = raw.decode('utf-16-le', errors='replace')
                except:
                    html = raw.decode('utf-8', errors='replace')
                
                if 'linenums' in html:
                    format_counts['linenums'] += 1
                    if len(sample_files['linenums']) < 3:
                        sample_files['linenums'].append(f)
                if 'wiz-code-container' in html:
                    format_counts['wiz-code-container'] += 1
                    if len(sample_files['wiz-code-container']) < 3:
                        sample_files['wiz-code-container'].append(f)
                if 'highlighter-hljs' in html:
                    format_counts['highlighter-hljs'] += 1
                    if len(sample_files['highlighter-hljs']) < 3:
                        sample_files['highlighter-hljs'].append(f)
                if 'class="gutter"' in html:
                    format_counts['table-gutter'] += 1
                    if len(sample_files['table-gutter']) < 3:
                        sample_files['table-gutter'].append(f)
                if 'class="highlight"' in html:
                    format_counts['pre-highlight'] += 1
                    if len(sample_files['pre-highlight']) < 3:
                        sample_files['pre-highlight'].append(f)
        except:
            pass

for fmt, count in format_counts.items():
    print(f'{fmt}: {count} notes')
    print(f'  samples: {sample_files[fmt]}')
