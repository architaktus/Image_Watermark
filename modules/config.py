import os

# [directories]
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # 项目根目录
DATABASE_DIR = os.path.join(BASE_DIR, 'data', 'watermark.db')
IMAGE_TO_PROCESS_DIR = os.path.join(BASE_DIR, 'images', 'to_process')
IMAGE_SOURCE_DIR = os.path.join(BASE_DIR, 'images', 'source')
IMAGE_WATERMARKED_DIR = os.path.join(BASE_DIR, 'images', 'watermarked')
QRCODE_DIR = os.path.join(BASE_DIR, 'data', 'qrcode')


TEST_ORIGINAL_DIR = os.path.join(BASE_DIR, 'images', 'source', 'DD_Material.jpg')
TEST_WATERMARKED_DIR = os.path.join(BASE_DIR, 'images', 'watermarked', 'DD_Material.jpg')
TEST_QR_DIR1 = os.path.join(IMAGE_WATERMARKED_DIR, 'LL.png')
TEST_QR_DIR2 = os.path.join(IMAGE_WATERMARKED_DIR, 'LH.png')
TEST_QR_DIR3 = os.path.join(IMAGE_WATERMARKED_DIR, 'QR.png')
TEST_QR_DIR4 = os.path.join(IMAGE_WATERMARKED_DIR, 'QR-temp-exact.png')

# [settings]
LOG = True


# [data]
AUTHOR = "Zhixi Xu"
COPYRIGHT_YEAR = "2024"

# rights_usage_terms
RIGHTS_USAGE_TERMS = "All rights reserved. Unauthorized reproduction, distribution, personal or commercial usage of this image is strictly prohibited. This image is also not permitted for use in training artificial intelligence or machine learning models. Any violation will be pursued under applicable copyright laws."

# contents
COPYRIGHT_QR = f"©{AUTHOR} {COPYRIGHT_YEAR}"
COPYRIGHT_SHORT = f"©{AUTHOR} {COPYRIGHT_YEAR}.  All rights reserved."
COPYRIGHT_LONG = f"©{AUTHOR} {COPYRIGHT_YEAR}.  {RIGHTS_USAGE_TERMS}"


# 全局动态配置
runtime_config = {
    "WM_ID": "",            # 水印id (对应db_utils中的watermark表格的watermark_id)
    "WM_FILE_NAME": "",     # 水印文件名 (对应db_utils中的watermark表格的watermark_file_name)
    "WM_FILE_DIR": "",      # 水印地址
    "WM_INFO_ALPHA": {      # 水印DWT处理的alpha值
        "ALPHA_LL": 0.1,
        "ALPHA_LH": 0.1,
        "ALPHA_HL": 0.1,
        },
    "WM_COLOR_PAD": 1,      # 默认拓展色彩 1黑白二值的白色255
    "WM_COLOR_SHIFT":{      # 默认黑白二值的颜色偏移
        "VALUE_1": 80,         # 0> 黑色
        "VALUE_2": 20          # 1> 白色（255）
        }
}