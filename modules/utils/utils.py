import os
from configparser import ConfigParser
from modules import config
import numpy as np


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


# 将小图像以色块填充至大图像等大
def pad_image_to_match(image, target_shape, fill_value=0):
    """
    将二值化图像填充到目标大小。
    image: 待处理二值化小图像 (ndarray, 值为 0 或 1)
    target_shape: 目标形状 (height, width)
    fill_value: 填充值 (默认为0)
    """
    target_height, target_width = target_shape
    wm_height, wm_width = image.shape

    # 计算上下和左右的填充大小
    pad_top = (target_height - wm_height) // 2
    pad_bottom = target_height - wm_height - pad_top
    pad_left = (target_width - wm_width) // 2
    pad_right = target_width - wm_width - pad_left

    # 填充水印
    padded_image = np.pad(
        image, 
        ((pad_top, pad_bottom), (pad_left, pad_right)), 
        mode='constant', 
        constant_values=fill_value
    )
    return padded_image