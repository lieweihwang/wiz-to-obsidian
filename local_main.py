"""
本地模式主入口。

从本地为知笔记数据目录直接读取笔记，无需登录为知服务器。

使用方式：
    python local_main.py

配置（在 .env 文件中新增）：
    WIZ_LOCAL_PATH=D:\\gitstore\\wiz\\My Knowledge\\Data\\18161262536
"""

import os
import sys
from log import log
from sync.init_dirs import init_output_dirs
from sync.database import Database
from sync.local_wiz_reader import LocalWizReader
from sync.local_note_synchronizer import LocalNoteSynchronizer
from dotenv import load_dotenv


def get_local_path() -> str:
    """从 .env 文件或环境变量读取本地为知笔记数据路径。"""
    # 定位 .env 文件（与 local_main.py 同级目录）
    if getattr(sys, 'frozen', False):
        app_root = os.path.dirname(sys.executable)
    else:
        app_root = os.path.dirname(os.path.abspath(__file__))

    dotenv_path = os.path.join(app_root, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path, override=True)

    local_path = os.getenv('WIZ_LOCAL_PATH', '').strip()
    if not local_path:
        raise ValueError(
            "请在 .env 文件中设置 WIZ_LOCAL_PATH，例如：\n"
            "WIZ_LOCAL_PATH=D:\\\\gitstore\\\\wiz\\\\My Knowledge\\\\Data\\\\18161262536"
        )
    if not os.path.isdir(local_path):
        raise FileNotFoundError(f"WIZ_LOCAL_PATH 目录不存在: {local_path}")

    return local_path


def main():
    log.info("=== wiz2obsidian 本地模式启动 ===")

    # 初始化输出目录
    app_root = init_output_dirs()
    log.info(f"应用根目录: {app_root}")

    # 读取本地路径配置
    local_path = get_local_path()
    log.info(f"本地为知笔记路径: {local_path}")

    # 创建本地读取器
    reader = LocalWizReader(local_path)

    # 启动同步
    with Database() as db:
        db.init()
        synchronizer = LocalNoteSynchronizer(reader, db)
        synchronizer.synchronize_notes()

    log.info("=== 本地模式转换完成，输出目录: output/note/ ===")


if __name__ == '__main__':
    main()
