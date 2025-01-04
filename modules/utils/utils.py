import os
import cv2
from configparser import ConfigParser
from modules import config
import numpy as np
from PIL import Image
from turbojpeg import TurboJPEG, TJPF_GRAY, TJSAMP_444

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



# 预处理
# 提取图片Y通道
def preprocess_image(image_path):
    """
    加载并预处理图像、转换为 YCbCr 色彩空间
    返回 Y, Cb, Cr 三通道
    """    
    print("读取图像...")
    try:
        # 图像为YCbCR格式时
        # 初始化 TurboJPEG 实例
        jpeg = TurboJPEG()
        # 读取 JPEG 文件
        with open(image_path, "rb") as jpeg_file:
            # 解码为 YCbCr 格式，单独提取Y通道（图像为RGB/CMYK等格式时自动转换）
            jpeg_data = jpeg_file.read()            
            print(f"    图片格式为YCbCR, 正在获取 Y 通道...")
            Y = jpeg.decode(jpeg_data, pixel_format=TJPF_GRAY)

            # 提取 其余 通道
            print(f"    获取 Cb, Cr 通道...")
            image = cv2.imread(image_path)
            ycbcr = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
            _, Cb, Cr = cv2.split(ycbcr)
    except:
        # 若TurboJPEG出错，使用转换方法
        print(f"    使用TurboJPEG读取异常(Turbo异常, 或图片非 YCbCR格式), 正在转换为YCbCR并提取 Y 通道...")
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f" 无法读取图像: {image_path}")
            # 转换为 YCbCr 色彩空间
            ycbcr = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
            # 提取三通道
            Y, Cb, Cr = cv2.split(ycbcr)
        except Exception as cv_err:
            raise RuntimeError(f"   图像处理失败: {cv_err}") from e
    
    # 检查矩阵维度
    if Y.ndim == 3:
        Y = Y.squeeze()  #移除最后一维
        print(f"    调整矩阵形状为{Y.shape}")
    return Y, Cb, Cr


# 拼接
def merge_image_left_and_right(left, right):
    """
    拼接左右图像
    返回 完整图像
    """
    # 确保左右部分的高度相同
    if left.shape[0] != right.shape[0]:
        # TODO 扩展
        raise ValueError("左右部分的高度不一致，无法合并")
    # 合并左右部分
    reconstructed_image = np.concatenate((left, right), axis=1)  # axis=1 水平拼接

    return reconstructed_image




# 提取查找带水印图片对应的原图
# TODO
    # TODO 查找db相应的img_id










# 水印预处理
def watermark_preprocess() -> np.ndarray:
    """
    水印预处理
        - 载入水印（二值二维码）
        - 转化为二值矩阵

    Returns:
        np.ndarray: 返回水印
    """
    print("     矩阵化水印")
    try:
        # 加载水印
        watermark_path = config.runtime_config['WM_FILE_DIR']
            # 使用 PIL 加载水印并保留 1 位数据
        watermark_img = Image.open(watermark_path).convert("1")  # 转为 1 位模式

        # 矩阵化
            # 转换为 NumPy 数组（无符号 8位整数：黑色像素为 0，白色像素为 255）
        watermark = np.array(watermark_img, dtype=np.uint8)
            # 将布尔值转换为 0 和 1 的形式（黑色像素 0 -> 0，白色像素 255 -> 1）
        watermark = (watermark > 0).astype(np.uint8)
            # 反色处理———— 0 > 1，1 > 0
        #watermark = 1 - watermark
        
        watermark_img.close()
        return watermark
    
    except FileNotFoundError:
        raise FileNotFoundError(f"水印文件未找到：{config.runtime_config['WM_FILE_DIR']}")
    

# 适配水印大小


# 替换水印色彩
def watermark_shift_color(watermark: np.ndarray) -> np.ndarray:
    """
    水印色彩处理 - 将黑白二值转换为合适的 8 位灰度中值

    Args:
        value_1 (int): 水印0对应值
        value_2 (int): 水印1对应值

    Returns:
        np.ndarray: 返回水印
    """
    # 替换水印值
    print("     替换水印色彩")
    watermark[watermark == 0] = config.runtime_config["WM_COLOR_SHIFT"]["VALUE_1"]
    watermark[watermark == 1] = config.runtime_config["WM_COLOR_SHIFT"]["VALUE_2"]

    watermark_lh_hl_img = Image.fromarray(watermark)
# TEST
    watermark_lh_hl_img.save(os.path.join(config.IMAGE_WATERMARKED_DIR, 'QR-色彩替换.png'))

    return watermark



# 将小图像扩充至目标大小
def pad_image_to_match(
        image: np.ndarray, 
        target_shape: tuple, 
        expand_type=[0,0], 
        random_fill=False, 
        pad_mode='constant'
    ) -> np.ndarray:
    """
    将二值化图像 (image) 填充到目标大小 (target_shape)。调整水印大小与目标子带匹配
        - 扩展尺寸
        - 填充内容

    Args:
        image: 待处理二值化小图像 (ndarray, 值为 0 或 1)
        target_shape: 目标形状 (height, width)
        expand_type: 填充形式：[x,y]方向拓展指令
            0 = 居中、拓展左右/上下； 
            1 = 居右/下，拓展左/上侧；
            2 = 居左/上，拓展右/下侧
        random_fill: True则填充随机噪点(默认为False)
        fill_value: 填充值 (默认为0)
        pad_mode: np.pad 的 mode 参数，支持 'constant'（默认），'reflect', 'wrap' 等

    Returns:
        np.ndarray: 返回拓展至目标大小的二值化图像Padded binary image of shape target_shape.
    """
    print(f"     调整水印尺寸({image.shape})为{target_shape}")
    ###################
    #拓展
    ###################
    # 尺寸
    target_height, target_width = target_shape
    wm_height, wm_width = image.shape
    #print(f"scale = {scale}, Yshape = {Y.shape}, LLshape = {LL.shape}, HLshape = {HL.shape}, LHshape = {LH.shape}, wm_array = {wm_array.shape}")

    # 计算比例
    scale = min(target_height / wm_height, target_width / wm_width)
    # 比例适配
        #不放大
    if scale >= 1 and scale < 2:  
        image_resized = image
    else:
        #缩小
        if scale <= 1:  
            #INTER_AREA 用于图像缩小的插值参数
            print("正在缩小水印")
            wm_resized_height = int(wm_height * scale)
            wm_resized_width = int(wm_width * scale)
            image_resized = cv2.resize(image, (wm_resized_width, wm_resized_height), interpolation=cv2.INTER_AREA)
        #略放大
        if scale >= 2:  
            print("正在放大水印")
            wm_resized_small_height = int(wm_height * scale  * 0.5)
            wm_resized_small_width = int(wm_width * scale  * 0.5)
            image_resized = cv2.resize(image, (wm_resized_small_width, wm_resized_small_height))
 
    ###################
    # 填充   
    ###################
    # 计算上下和左右的填充大小
    pad_y = target_height - wm_height
    pad_x = target_width - wm_width
        # 映射填充位置（原以条件分支判断，现优化为映射关系）
    expand_map = {0: lambda m: m // 2, 1: lambda m: m, 2: lambda m: 0}  # 映射+ 匿名函数x3
    pad_left = expand_map.get(expand_type[0], expand_map[0])(pad_x)     # x方向：如果 expand_type[0] 不存在，返回默认值 expand_map[0]
    pad_top = expand_map.get(expand_type[1], expand_map[0])(pad_y)      # y方向：同理
    if expand_type[0] not in expand_map or expand_type[1] not in expand_map:
        print("WARNING: 填充位置设置错误! 已按居中设置")
    pad_bottom = pad_y - pad_top
    pad_right = pad_x - pad_left

    # 填充水印
        # 填充随机噪声  TODO 测试
    fill_value = config.runtime_config["WM_COLOR_PAD"]
    if random_fill and pad_mode == 'constant':
            #填充区域用随机噪声（值为 0 或 1）代替————dtype=np.uint8：指定生成的数组元素类型为 8 位无符号整数
        top_noise = np.random.randint(0, 2, (pad_top, wm_width), dtype=np.uint8)
        bottom_noise = np.random.randint(0, 2, (pad_bottom, wm_width), dtype=np.uint8)
        left_noise = np.random.randint(0, 2, (target_height, pad_left), dtype=np.uint8)
        right_noise = np.random.randint(0, 2, (target_height, pad_right), dtype=np.uint8)

            # 组合图像
        #padded_image = np.pad(image, ((0, 0), (pad_left, pad_right)), mode='constant', constant_values=0)
        padded_image = np.concatenate([top_noise, image_resized, bottom_noise], axis=0)  # 高度（第 0 维），拼接上下
        padded_image = np.concatenate([left_noise, image_resized, right_noise], axis=1)  # 宽度（第 1 维），拼接左右
    else:
        # 填充单色
        padded_image = np.pad(
            image_resized, 
            ((pad_top, pad_bottom), (pad_left, pad_right)), 
            mode=pad_mode, 
            constant_values=(fill_value if pad_mode == 'constant' else None)
        )

    return padded_image
