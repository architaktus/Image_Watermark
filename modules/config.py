import os

# [directories]
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # 项目根目录
DATABASE_DIR = os.path.join(BASE_DIR, 'data', 'project.db')
IMAGE_TO_PROCESS_DIR = os.path.join(BASE_DIR, 'images', 'to_process')
IMAGE_SOURCE_DIR = os.path.join(BASE_DIR, 'images', 'source')
IMAGE_WATERMARKED_DIR = os.path.join(BASE_DIR, 'images', 'watermarked')


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