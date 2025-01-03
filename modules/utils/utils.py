import os
from configparser import ConfigParser
from modules import config



# 操作日志/记录
def log_action(db_conn, action_type, description):
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO logs (action_type, description) VALUES (?, ?)", (action_type, description))
    db_conn.commit()

# 全局动态配置
def update_runtime_config(wm_id, wm_file_name):
    config.runtime_config["WM_ID"] = wm_id
    config.runtime_config["WM_FILE_NAME"] = wm_file_name
    config.runtime_config["WM_FILE_DIR"] = os.path.join(config.QRCODE_DIR, wm_file_name)

# 查找文件
def check_file_exists(file_path):
    """
    检查指定路径的水印文件是否存在。
    
    :param file_path: 文件的完整路径
    :return: 布尔值 True 表文件存在
    """
    return os.path.exists(file_path)