import os
import datetime
from sync.file_manager import FileManager
from log import log # 导入 log


class ImageHandler:

    @staticmethod
    def handle(record, image_name):
        """
        处理图片, 将文件重命名为: YYYYMMDDHHMMSSSSS.ext 并返回处理后的图片相对地址
        :param record: 笔记同步记录
        :param image_name: 图片名称
        :return: 处理后的图片相对地址 ./images/image_name.ext
        """
        base_img_directory = FileManager.get_img_directory(record)
        old_img_path = os.path.join(base_img_directory, image_name)

        # 检查旧文件是否存在
        if not os.path.exists(old_img_path):
            # 可以选择抛出异常或记录日志
            log.error(f"Error: Image file not found at {old_img_path}") # 使用 log.error
            return None # 或者根据需要返回错误指示

        # 提取文件扩展名
        _, ext = os.path.splitext(image_name)
        # 生成新文件名 (YYYYMMDDHHMMSSmmm)
        new_name_part = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
        new_image_name = f"{new_name_part}{ext}"
        new_img_path = os.path.join(base_img_directory, new_image_name)

        # 重命名文件
        try:
            os.rename(old_img_path, new_img_path)
            log.info(f"Image renamed from {old_img_path} to {new_img_path}") # 使用 log.info
        except OSError as e:
            log.error(f"Error renaming file {old_img_path} to {new_img_path}: {e}") # 使用 log.error
            return None # 或者根据需要返回错误指示

        # 返回相对路径 ./<notename>/new_image_name.ext
        # 匹配 Obsidian 附件路径配置: ${notepath}/${notename}
        # 注意: 这里必须使用 POSIX 风格的分隔符，以保证 Obsidian 等 Markdown 渲染器识别
        # 对路径中的空格进行 URL 编码（空格→%20），否则 Obsidian 无法解析 Markdown 图片链接
        safe_title = FileManager.sanitize_filename(record.get('title', 'images'))
        encoded_title = safe_title.replace(' ', '%20')
        relative_path = f"./{encoded_title}/{new_image_name}"
        return relative_path
