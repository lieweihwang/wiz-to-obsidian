import sys, os, zipfile, traceback
sys.stdout.reconfigure(encoding='utf-8')

ziw_path = r'D:\gitstore\wiz\My Knowledge\Data\18161262536\My Notes\架构和调优\QCon\QCon北京2016\打破规则，我是黑客专题\Hacking ipcam like Harold in POI——攻击智能摄像头-洪宇.ziw'

with zipfile.ZipFile(ziw_path, 'r') as zf:
    raw = zf.read('index.html')
    html = raw.decode('utf-16-le', errors='replace')

    from sync.note_parser_factory import NoteParserFactory
    from sync.local_wiz_reader import LocalWizReader
    reader = LocalWizReader(r'D:\gitstore\wiz\My Knowledge\Data\18161262536')
    note_type = reader.detect_type_from_html(html)
    print(f'检测到的类型: {note_type}')

    parser = NoteParserFactory.create_parser(note_type, 'Hacking ipcam')
    try:
        result = parser.process_content(html)
        print(f'解析成功! 内容长度: {len(result.content)} 字符')
        print(f'前200字符: {result.content[:200]}')
    except Exception as e:
        traceback.print_exc()
