import os
from configparser import ConfigParser
from PIL import Image

import pyexiv2


# 操作日志/记录
def log_action(db_conn, action_type, description):
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO logs (action_type, description) VALUES (?, ?)", (action_type, description))
    db_conn.commit()

#######################################################################################################################################
#######################################################################################################################################
# 加载配置


# 配置文件路径
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) # 项目根目录
CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'config.ini')

def load_config():
    # 创建配置解析器实例
    print(BASE_DIR)
    config = ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

    # 读取配置文件
    config.read(CONFIG_FILE)
    return config



#######################################################################################################################################
#######################################################################################################################################


# 检查 to_process 文件夹
def get_image_list(folder='to_process'):
    image_files = []
    for file in os.listdir(folder):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_files.append(os.path.join(folder, file))
    return image_files


# 提取图片元数据
def extract_metadata(image_path):
    metadata = {}
    with Image.open(image_path) as img:
        metadata['title'] = img.filename
        metadata['exif'] = img.info.get('exif', 'No EXIF found')
        try:
            with pyexiv2.Image(image_path) as meta_img:
                metadata['iptc'] = meta_img.read_iptc()
        except Exception as e:
            metadata['iptc'] = f"Error reading IPTC: {e}"
    return metadata


# 更新版权信息
def update_copyright(image_path, copyright_info):
    try:
        with pyexiv2.Image(image_path) as img:
            img.modify_exif({'Exif.Image.Copyright': copyright_info})
            img.write()
    except Exception as e:
        print(f"Error updating EXIF: {e}")