import numpy as np
import pywt     #DWT工具
import cv2
from PIL import Image
from io import BytesIO
from modules import config
from modules.utils import utils
#import matplotlib.pyplot as plt
import math 

###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################

# 嵌入水印
def stega_embed(image_path, output_path, embed_type=1, alpha=0.1, wavelet='haar'):
    """
    水印嵌入核心函数

    Args:
        embed_type: 1="LL"+"HL/LH"; 2="LL"; 3="HL/LH"

    Returns:
        返回加入水印的Y通道
    """
    # 读取图像，分通道
    Y, Cb, Cr = utils.preprocess_image(image_path)
    
    # 执行 1 级 DWT 分解
    coeffs = dwt_decompose(Y, wavelet)
    LL, _ = coeffs

    # 水印预处理
    print("预处理水印...")
    watermark = utils.watermark_preprocess()    
    watermark_resized = utils.pad_image_to_match(watermark, LL.shape)
    watermark_color_shifted = utils.watermark_shift_color(watermark_resized)

    # 嵌入水印
    print("嵌入水印...")
    Y_watermarked = embed_watermark(coeffs, watermark_color_shifted, embed_type, alpha)

    # 重构图像
    print("重构图像...")
    print(f"    Y通道 尺寸{Y_watermarked.shape}, 最大值 {np.max(Y_watermarked)}, 最小值 {np.min(Y_watermarked)}")
    print(f"    Cb通道 尺寸{Cb.shape}, 最大值 {np.max(Cb)}, 最小值 {np.min(Cb)}")
    print(f"    Cr通道 尺寸{Cr.shape}, 最大值 {np.max(Cr)}, 最小值 {np.min(Cr)}")
    Y_watermarked = np.clip(Y_watermarked, 0, 255).astype(np.uint8)
    ycbcr_watermarked = cv2.merge([Y_watermarked, Cb, Cr])
        # YCrCb 转 RGB
    watermarked_image = cv2.cvtColor(ycbcr_watermarked, cv2.COLOR_YCrCb2BGR)

    # 保存水印图像
    print("保存图像...")
    #cv2.imwrite(output_path, watermarked_image)
    cv2.imwrite(output_path, watermarked_image)
    print(f"水印写入成功！图像保存于{output_path}")



###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################

# 提取水印
def stega_extract(watermarked_image_path, origin_image_path, embed_type=1, alpha=0.1):
    """
    水印提取核心函数。根据带水印图片及对应的原图，提取图中的指定子带上的水印

    Args:
        watermarked_image_path: 带水印图片
        origin_image_path: 对应的原图
        embed_type: 水印嵌入类型
            1 = "LL"+"HL/LH"; 
            2 = "LL"; 
            3 = "HL/LH"
        alpha: 水印强度 # TODO

    Returns:
        返回水印图字典
            0: LL子带水印图
            1: LH/HL子带合并水印图
    """
    # 读取图像，分通道
    print("开始解析图像...")
    print("     分解目标图像亮度通道Y")
    print(f"    正在读取带水印图片...")
    Y_watermarked, _, _ = utils.preprocess_image(watermarked_image_path)
    print(f"    正在读取原始图片...")
    Y, _, _ = utils.preprocess_image(origin_image_path)


    # 提取水印
    if embed_type == 1 or embed_type == 2:
        print("     提取LL子带水印...")
        extracted_watermark_ll = extract_watermark(Y_watermarked, Y, "LL", alpha)
        #extracted_watermark_ll = np.clip(extracted_watermark_ll, 0, 1).astype(np.uint8)  # 确保提取结果为二值        
        extracted_watermark = np.clip(extracted_watermark_ll, 0, 255).astype(np.uint8)

        # 对所提取的水印，以 1 位 PNG 格式打包
        #cv2.imwrite('extracted_watermark.png', extracted_watermark)
        print("     提取成功，生成图像...")        
        watermark_ll_img = Image.fromarray(extracted_watermark_ll)
#        test
        watermark_ll_img.save(config.TEST_QR_DIR1)

    if embed_type == 1 or embed_type == 3:
        print("     正在提取LH/HL子带水印...")
        extracted_watermark_lh = extract_watermark(Y_watermarked, Y, "LH", alpha)
        extracted_watermark_hl = extract_watermark(Y_watermarked, Y, "HL", alpha)

        print("     提取成功，合成图像...")        
        print(extracted_watermark_lh.shape)
        h, w = extracted_watermark_lh.shape
        watermark_left = extracted_watermark_hl[:, :w//2]  # 左部分
        watermark_right = extracted_watermark_lh[:, w//2:]  # 右部分
        extracted_watermark_lh_hl = utils.merge_image_left_and_right(watermark_left, watermark_right)
        extracted_watermark_lh_hl = np.clip(extracted_watermark_lh_hl, 0, 1).astype(np.uint8)  # 确保提取结果为二值

        # 输出
            # 将 NumPy 数组转换为 PIL.Image.Image 对象
        watermark_lh_hl_img = Image.fromarray(extracted_watermark_lh_hl * 255).convert("1")
        
#        # 对所提取的水印，以 1 位 PNG 格式打包
        watermark_lh_hl_img.save(config.TEST_QR_DIR2)
    
    #返回字典
    result = {}
    if watermark_ll_img:
        result[0] = watermark_ll_img
    #if watermark_lh_hl_img:
        #result[1] = watermark_lh_hl_img
    return result
    # TODO 显示在GUI上





###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################
# 相关函数  ################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################
###########################################################################################################


#####################################################################################
# DWT 双向过程


# DWT 分解
def dwt_decompose(image:np.ndarray, wavelet='haar', level=1):
    """
    DWT 分解
    返回 包含LL, (LH, HL, HH) 两组频带组的数列coeffs
    """
    coeffs = pywt.wavedec2(image, wavelet, level=level)
    #LL, (LH, HL, HH) = coeffs   # 将 coeffs[0] 解包到变量 LL，将 coeffs[1] 中的三个值分别解包到 LH, HL, 和 HH。
    #return LL, LH, HL, HH
    return coeffs

# DWT 重建
def dwt_reconstruct(coeffs, wavelet='haar'):
    reconstructed = pywt.waverec2(coeffs, wavelet)
    return reconstructed
#def apply_idwt(LL, LH, HL, HH):
#    """重构图像"""
#    coeffs = (LL, (LH, HL, HH))
#    reconstructed = pywt.idwt2(coeffs, 'haar')
#    return np.uint8(np.clip(reconstructed, 0, 255))




#####################################################################################
#####################################################################################
#####################################################################################
# 正向：水印嵌入

# 水印嵌入
def embed_watermark(
        coeffs:list, 
        wm_array:np.ndarray, 
        embed_type:int, 
        alpha=0.1, 
        wavelet='haar'
    )->np.ndarray:
    """
    水印嵌入
    返回 加入水印的Y通道
    :param wm_array: 矩阵化的水印图
    :param embed_type: 水印嵌入类型
            1 = "LL"+"HL/LH"; 
            2 = "LL"; 
            3 = "HL/LH"
    """
    LL, (LH, HL, HH) = coeffs
    Y_1= dwt_reconstruct(coeffs, wavelet)
    print(f"test原尺寸 {Y_1.shape}")

    # 分类嵌入水印
    # 嵌入水印到 LL 子带
    if embed_type == 1 or embed_type == 2:
        print("     嵌入LL子带")
        LL_watermarked = LL + alpha * wm_array
        LL_watermarked[LL_watermarked > 255 ] = 255
        LL_watermarked[LL_watermarked < 0 ] = 0
        # 用修改后的 LL 替换
        coeffs[0] = LL_watermarked
    
    # 嵌入水印到 HL/LH 子带
    if embed_type == 1 or embed_type == 3:
        print("     嵌入HL/LH子带")
        # 将水印左右等分，且保持原尺寸但通过留白拓展为完整尺寸
        h, w = wm_array.shape
        wm_array_left = wm_array[:, :w//2]  # 左部分
        wm_array_right = wm_array[:, w//2:]  # 右部分

        # 留白扩展
        wm_array_left_matched = utils.pad_image_to_match(wm_array_left, LL.shape, [2,0])
        wm_array_right_matched = utils.pad_image_to_match(wm_array_right, LL.shape, [1,0])

        # 分别嵌入 HL 和 LH 子带
        HL_watermarked = HL + alpha * wm_array_left_matched #二维码左半在HL
        LH_watermarked = LH + alpha * wm_array_right_matched #二维码右半在LH
        coeffs[1] = (LH_watermarked, HL_watermarked, HH)    

    # 逆 DWT 重建图像
    print("     逆DWT, 重建Y通道")
    Y_watermarked = dwt_reconstruct(coeffs, wavelet)
    print(f"test新尺寸 {Y_watermarked.shape}")

    return Y_watermarked




#####################################################################################
#####################################################################################
#####################################################################################
# 逆过程：水印提取


# 依赖原图
def extract_watermark(Y_watermarked, Y_original, subband_type, alpha=0.1, tolerance =8, wavelet='haar')->np.ndarray:
    """
    根据带水印图片及对应的原图，提取图中的指定子带上的水印
    先提取子带(type: ndarray)

    Args:
        watermarked_image_path: 带水印图片
        origin_image_path: 对应的原图
        subband_type: 指定子带, "LL""LH""HL""HH"
        alpha: 水印强度

    Returns:
        返回水印图
    """
    # 对嵌入后的和原始的 Y 通道进行 DWT
    coeffs_watermarked = dwt_decompose(Y_watermarked, wavelet)
    coeffs_original = dwt_decompose(Y_original, wavelet)

    # 选择子带——原始办法
    if subband_type == "LL":
        subband_watermarked = coeffs_watermarked[0]
        subband_original = coeffs_original[0]
        print(subband_watermarked.shape)
        print(subband_original.shape)
    if subband_type == "HL":
        subband_watermarked = coeffs_watermarked[0][0]
        subband_original = coeffs_original[0][0]
        print(subband_watermarked.shape)
        print(subband_original.shape)
    if subband_type == "LH":
        subband_watermarked = coeffs_watermarked[0][1]
        subband_original = coeffs_original[0][1]
        print(subband_watermarked.shape)
        print(subband_original.shape)
    if subband_type == "HH":
        subband_watermarked = coeffs_watermarked[0][2]
        subband_original = coeffs_original[0][2]
        print(subband_watermarked.shape)
        print(subband_original.shape)

    #print(type(subband_watermarked))
    #print(subband_watermarked.shape) 
    #print(type(subband_original))
    #print(subband_original.shape) 

    # 提取水印
        # 参数
    value_1 = config.runtime_config["WM_COLOR_SHIFT"]["VALUE_1"]
    value_2 = config.runtime_config["WM_COLOR_SHIFT"]["VALUE_2"]
        # 恢复水印矩阵
    diff = subband_watermarked - subband_original
    #watermark_extracted = diff / alpha
    watermark_extracted = np.round(diff / alpha)    #四舍五入
        # value_1 二维码黑色部分/取值大者 ———— 超过value_2（含误差）的肯定都是value_1所属
    watermark_extracted[watermark_extracted > (value_2 + tolerance) ] = value_1
        # value_2 二维码白色部分/取值小者 
        # ———— 一些噪点以及原嵌入过程中处于255（叠加）、0（相减）附近的像素，作为误差，可部分纳入value_2所属
    watermark_extracted[(watermark_extracted <= (value_2 + math.ceil(tolerance / 1.5)))  & \
                        (watermark_extracted >= (value_2 - math.ceil(tolerance / 1.5)))] = value_2    # //向下取整, math.ceil向上取整
                        #(watermark_extracted >= (value_2 - tolerance // 1.5))] = value_2    # //向下取整, math.ceil向上取整
    watermark_extracted = watermark_extracted.astype(np.uint8)
        # 反向还原为 黑白/0 和 1/0 255
    watermark_extracted[watermark_extracted == value_1] = 0
    watermark_extracted[watermark_extracted == value_2] = 255
    
    #print(type(watermark_extracted))
    #print(watermark_extracted.shape) 

    return watermark_extracted


# 逆过程：水印提取(盲提取)
def extract_watermark_blind(Y_watermarked, alpha=0.1, wavelet='haar'):
    # 对嵌入后的和原始的 Y 通道进行 DWT
    coeffs_watermarked = dwt_decompose(Y_watermarked, wavelet)
    LH_watermarked, HL_watermarked, _ = coeffs_watermarked[1]

    # 提取水印
    watermark_extracted = (HL_watermarked + LH_watermarked) / (2 * alpha)

    return watermark_extracted



#####################################################################################
# TODO GUI

