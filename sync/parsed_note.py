from __future__ import annotations
from log import log
import re


class ParsedNote:
    def __init__(self, content, need_upload_images):
        self.content = content
        self.need_upload_images = need_upload_images

    def replace_image_url(self, origin_img_image_url_map: dict[str, str]):
        """
        替换md文件中的图片链接中的地址。
        :param origin_img_image_url_map: {img_name: upload_url}

        注意：need_upload_images 中的图片名已经是反转义后的原始文件名（如 302125145008842[1].png），
        但 Markdown 内容中 html2text 生成的仍是转义形式（302125145008842\[1\].png）。
        因此替换时需要同时尝试两种形式。
        """
        log.info(f'需要上传的图片集合：{self.need_upload_images}')
        for img_name in self.need_upload_images:
            if img_name not in origin_img_image_url_map:
                log.info(f'图片：{img_name} 不存在')
                continue
            target_url = origin_img_image_url_map[img_name]
            # 原始文件名（用于在内容中直接匹配）
            # 转义形式：html2text 将 [ ] 转义为 \[ \]
            escaped_name = img_name.replace('[', r'\[').replace(']', r'\]')
            for name in (img_name, escaped_name):
                self.content = self.content.replace(f'(index_files/{name})', f'({target_url})')
                self.content = self.content.replace(f'({name})', f'({target_url})')