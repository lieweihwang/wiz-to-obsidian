# wiz2obsidian

将为知笔记（WizNote）的所有笔记导出为 Obsidian 兼容的 Markdown 文件，支持**在线模式**和**本地模式**两种方式。

## ✨ 特性

- 🔄 **双模式运行**：支持通过 API 在线导出，也支持直接读取本地 `.ziw` 文件离线导出
- 📝 **多笔记类型**：HTML 笔记、Lite/Markdown 笔记、协作笔记全部支持
- 🖼️ **图片与附件**：自动提取并保存到笔记同名子文件夹，匹配 Obsidian 附件路径配置 `${notepath}/${notename}`
- 🔗 **内部链接转换**：`wiz://` 内链自动转为 Obsidian `[[双链]]` 格式
- 💻 **6 种代码块格式**：完美识别 WizNote 的 Prettify、CodeMirror、hljs、博客表格、Hexo highlight、wiz-editor-doc 等代码块格式
- 📊 **表格保护**：智能处理 WizNote 新版编辑器嵌套 div 表格，防止结构被破坏
- 🧹 **格式清理**：自动清理 WizNote 残留标签、CSS、占位符，输出干净的 Markdown
- 📦 **增量同步**：通过 SQLite 记录同步状态，支持断点续传

## 📋 前置准备

### 在线模式

1. 将所有加密笔记取消加密
2. 在 [releases 页面](https://github.com/awaken233/wiz2obsidian/releases)下载对应系统的可执行文件
3. 在可执行文件同级目录下创建 `.env` 文件，配置为知笔记的用户名和密码：
   ```env
   userId=your_wiznote_email
   password=your_password
   ```
4. 将设置-安全选项-[登录二次验证暂时关闭](https://github.com/awaken233/wiz2obsidian/issues/16)
5. 运行可执行文件

### 本地模式（推荐）

无需登录为知服务器，直接读取本地数据目录：

1. 找到为知笔记本地数据目录，通常位于：
   - Windows：`C:\Users\<用户名>\Documents\My Knowledge\Data\<用户ID>`
   - macOS：`~/Library/Application Support/WizNote/Data/<用户ID>`
2. 在 `.env` 文件中配置路径：
   ```env
   WIZ_LOCAL_PATH=D:\path\to\My Knowledge\Data\18161262536
   ```
3. 运行：
   ```bash
   python local_main.py
   ```

## 📁 输出结构

```
output/
├── db/
│   └── sync.db            # SQLite 同步状态记录
├── note/                  # 导出的 Markdown 笔记
│   └── My Notes/
│       └── 分类目录/
│           ├── 笔记标题.md
│           └── 笔记标题/    # 图片和附件（与笔记同名文件夹）
│               ├── 20260616120000123.png
│               └── attachment.pdf
└── log/
    └── log_2026-06-16.log  # 日志
```

> 图片和附件统一放在与笔记同名的子文件夹中，匹配 Obsidian 附件路径配置 `${notepath}/${notename}`。

## 🔧 笔记类型处理

### HTML 笔记（document）

使用 `html2text` 将 HTML 转换为 Markdown，并进行深度预处理：

**代码块处理** — 支持 WizNote 的 6 种代码存储格式：

| 格式 | HTML 特征 | 来源 |
|------|----------|------|
| Google Prettify | `<pre class="prettyprint linenums">` | WizNote 内建 |
| CodeMirror | `<div class="wiz-code-container">` | WizNote 内建 |
| hljs | `<pre class="highlighter-hljs">` | 剪藏文章 |
| Table gutter+code | `<td class="gutter">` + `<td class="code">` | 博客剪藏 |
| Hexo highlight | `<div class="highlight"> > <code class="language-xxx">` | 博客剪藏 |
| wiz-editor-doc | `<wiz-editor-doc data-source="...">` | 新版编辑器 |

**其他预处理**：
- 新版编辑器 `editor-container` 嵌套 div 表格简化
- 表格单元格内 `<br>` 清理
- wiz-todo CSS 残留清理
- 空图片引用清除
- 图片路径空格 URL 编码
- JSON 语言自动识别

### Lite 笔记（lite/markdown）

从 `<pre>` 标签直接提取原始 Markdown 内容。

### 协作笔记（collaboration）

通过自定义 JSON 解析器处理，支持：
- 文本、标题、引用、列表（有序/无序/复选框）
- 代码块（含语言标识）、表格
- 图片、附件、流程图、Mermaid
- 数学公式（LaTeX → `$...$`）
- 内嵌网页、评论（含 @提及和时间戳）
- WikiLink 双链

## ⚠️ 注意事项

- 笔记标题中的特殊字符（`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`）会自动替换为 `_`
- 为知笔记应用不要打开协作笔记 tab 页，否则影响程序读取数据
- 加密笔记请先取消加密后再导出
- 本地模式不支持协作笔记（需要网络通信）

## 🛠️ 开发

### 环境搭建

```bash
# 克隆项目
git clone https://github.com/awaken233/wiz2obsidian.git
cd wiz2obsidian

# 安装依赖
pip install -r requirements.txt
```

### 项目结构

```
wiz2obsidian/
├── main.py                     # 在线模式入口
├── local_main.py               # 本地模式入口
├── sync/                       # 核心同步逻辑
│   ├── html_note_parser.py     # HTML→Markdown 转换（6 种代码块格式）
│   ├── lite_note_parser.py     # Lite 笔记解析
│   ├── collaboration_note_parser.py  # 协作笔记 JSON 解析
│   ├── note_parser_factory.py  # 解析器工厂
│   ├── note_fixer.py           # Markdown 后处理修复
│   ├── image_handler.py        # 图片重命名与路径生成
│   ├── file_manager.py         # 文件 I/O 与路径管理
│   ├── wiz_link_resolver.py    # wiz:// 链接→Obsidian [[]] 转换
│   ├── local_wiz_reader.py     # 本地 .ziw 文件读取器
│   ├── local_note_synchronizer.py  # 本地模式同步器
│   ├── note_synchronizer.py    # 在线模式同步器
│   ├── wiz_open_api.py         # 为知笔记 API 客户端
│   ├── database.py             # SQLite 同步状态管理
│   └── config.py               # 配置管理
├── conf/
│   └── logging.yaml            # 日志配置
├── test/                       # 测试文件
└── .env                        # 环境配置（不提交）
```

### 打包

```bash
# 使用打包脚本
python build.py

# 或手动使用 PyInstaller
pyinstaller --clean wiz2obsidian.spec
```

打包后可执行文件位于 `dist/` 目录。

## 📚 参考

- [WizNote macOS 本地文件夹分析 | ZRONG's BLOG](https://blog.zengrong.net/post/analysis-of-wiznote/)
- [wiz-editor 服务架构](https://github.com/WizTeam/wiz-editor/blob/main/docs/zh-CN/server-architecture.md)
- [WizTeam/wiz-editor](https://github.com/WizTeam/wiz-editor)
- [为知笔记 API 文档](https://www.wiz.cn/wapp/pages/book/bb8f0f10-48ca-11ea-b27a-ef51fb9d4bb4/475c9ef0-4e1a-11ea-8f5c-a7618da01da2)

## 📄 许可证

[MIT License](LICENSE)
