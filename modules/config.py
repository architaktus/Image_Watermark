import os

# [directories]
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # 项目根目录
DATABASE_DIR = os.path.join(BASE_DIR, 'data', 'watermark.db')
IMAGE_TO_PROCESS_DIR = os.path.join(BASE_DIR, 'images', 'to_process')
IMAGE_SOURCE_DIR = os.path.join(BASE_DIR, 'images', 'source')
IMAGE_WATERMARKED_DIR = os.path.join(BASE_DIR, 'images', 'watermarked')
QRCODE_DIR = os.path.join(BASE_DIR, 'data', 'qrcode')


# [settings]
LOG = True


# [data]
AUTHOR = "Zhixi Xu"
COPYRIGHT_YEAR = "2024"

# rights_usage_terms
RIGHTS_USAGE_TERMS = "All rights reserved. Unauthorized reproduction, distribution, personal or commercial usage of this image is strictly prohibited. This image is also not permitted for use in training artificial intelligence or machine learning models. Any violation will be pursued under applicable copyright laws."

# contents
COPYRIGHT_SHORT = f"©{AUTHOR} {COPYRIGHT_YEAR}.  All rights reserved."
COPYRIGHT_LONG = f"©{AUTHOR} {COPYRIGHT_YEAR}.  {RIGHTS_USAGE_TERMS}"


# 全局动态配置
runtime_config = {
    "WM_ID": "",    #水印id (对应db_utils中的watermark表格的watermark_id)
    "WM_FILE_NAME": "",    #水印文件名 (对应db_utils中的watermark表格的watermark_file_name)
    "WM_FILE_DIR": "",    #水印地址
    "WM_INFO_ALPHA": "",    #水印DWT处理的alpha值
}