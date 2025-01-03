import numpy as np
import pywt     #DWT工具
import cv2
from PIL import Image
from io import BytesIO
from modules import config
from modules.utils import utils
#import matplotlib.pyplot as plt

# 预处理
def preprocess_image(image_path):
    """
    加载并预处理图像、转换为 YCbCr 色彩空间
    返回 Y, Cb, Cr 三通道
    """
    # 读取图像
    image = cv2.imread(image_path)
    # 转换为 YCbCr 色彩空间
    ycbcr = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    # 提取 Y 通道
    Y, Cb, Cr = cv2.split(ycbcr)
    return Y, Cb, Cr


#####################################################################################
# DWT 分解
def dwt_decompose(image, wavelet='haar', level=1):
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
# 水印嵌入
def embed_watermark(Y, watermark, embed_type, alpha=0.1, wavelet='haar'):
    """
    水印嵌入
    返回 加入水印的Y通道
    """
    # 执行 1 级 DWT 分解
    coeffs = dwt_decompose(Y, wavelet)
    LL, (LH, HL, HH) = coeffs

    # 调整水印大小与目标子带匹配
    img_height, img_width = LL.shape
    wm_height, wm_width = watermark.shape
    #print(f"scale = {scale}, Yshape = {Y.shape}, LLshape = {LL.shape}, HLshape = {HL.shape}, LHshape = {LH.shape}, watermark = {watermark.shape}")
    scale = min(img_height / wm_height, img_width / wm_width)
    if scale >= 1 and scale < 2:  #不放大
        watermark_resized = watermark
    else:
        if scale <= 1:  #缩小
            #INTER_AREA 用于图像缩小的插值参数
            print("正在缩小水印")
            wm_resized_height = int(wm_height * scale)
            wm_resized_width = int(wm_width * scale)
            watermark_resized = cv2.resize(watermark, (wm_resized_width, wm_resized_height), interpolation=cv2.INTER_AREA)
        if scale >= 2:  #略放大
            print("正在放大水印")
            wm_resized_small_height = int(wm_height * scale  * 0.5)
            wm_resized_small_width = int(wm_width * scale  * 0.5)
            watermark_resized = cv2.resize(watermark, (wm_resized_small_width, wm_resized_small_height))
    # 填充水印至图像等大
    watermark_resized_matched = utils.pad_image_to_match(watermark_resized, LL.shape)

    # 分类嵌入水印
    # 嵌入水印到 LL 子带
    if embed_type == 1 or embed_type == 3:
        print("DWT: 嵌入LL子带")
        LL_watermarked = LL + alpha * watermark_resized_matched
        # 用修改后的 LL 替换
        coeffs[0] = LL_watermarked
    
    # 嵌入水印到 HL/LH 子带
    if embed_type == 2 or embed_type == 3:
        print("DWT: 嵌入HL/LH子带")
        HL_watermarked = HL + alpha * watermark_resized_matched
        LH_watermarked = LH + alpha * watermark_resized_matched
        coeffs[1] = (LH_watermarked, HL_watermarked, HH)    

    # 逆 DWT 重建图像
    print("逆DWT 重建Y通道")
    Y_watermarked = dwt_reconstruct(coeffs, wavelet)
    return Y_watermarked



#####################################################################################
# 逆过程：水印提取(依赖原图)
def extract_watermark_ll(Y_watermarked, Y_original, alpha=0.1, wavelet='haar'):
    # 对嵌入后的和原始的 Y 通道进行 DWT
    coeffs_watermarked = dwt_decompose(Y_watermarked, wavelet)
    coeffs_original = dwt_decompose(Y_original, wavelet)
    LL_watermarked, _ = coeffs_watermarked
    LL_original, _ = coeffs_original

    # 提取水印
    watermark_extracted = (LL_watermarked - LL_original) / alpha

    return watermark_extracted

# 逆过程：水印提取(盲提取)
def extract_watermark_hl(Y_watermarked, alpha=0.1, wavelet='haar'):
    # 对嵌入后的和原始的 Y 通道进行 DWT
    coeffs_watermarked = dwt_decompose(Y_watermarked, wavelet)
    LH_watermarked, HL_watermarked, _ = coeffs_watermarked[1]

    # 提取水印
    watermark_extracted = (HL_watermarked + LH_watermarked) / (2 * alpha)

    return watermark_extracted


#####################################################################################
# 主程序
def stega_embed(image_path, output_path, embed_type=3, alpha=0.1):
    """
    水印嵌入
    返回 加入水印的Y通道
    :param embed_type: 1="LL"+"HL/LH"; 2="LL"; 3="HL/LH"
    """
    watermark_path = config.runtime_config['WM_FILE_DIR']

    # 读取图像，分通道
    Y, Cb, Cr = preprocess_image(image_path)

    # 使用 PIL 加载水印并保留 1 位数据
    watermark_img = Image.open(watermark_path).convert("1")  # 转为 1 位模式
    # 矩阵化
        # 转换为 NumPy 数组（黑色像素为 0，白色像素为 255）>（无符号 8位整数）
    watermark = np.array(watermark_img, dtype=np.uint8)
        # 将布尔值转换为 0 和 1 的形式
    watermark = (watermark > 0).astype(np.uint8)

    # 嵌入水印
    Y_watermarked = embed_watermark(Y, watermark, embed_type, alpha)

    # 重构图像
    Y_watermarked = np.clip(Y_watermarked, 0, 255).astype(np.uint8)
    ycbcr_watermarked = cv2.merge([Y_watermarked, Cb, Cr])
    watermarked_image = cv2.cvtColor(ycbcr_watermarked, cv2.COLOR_YCrCb2BGR)

    # 保存水印图像
    cv2.imwrite(output_path, watermarked_image)


# TODO GUI
def stega_extract(image_path_watermarked, image_path_origin, subband_type, alpha=0.1):
    # TODO 查找db相应的img_id
    # 读取图像，分通道
    Y_watermarked, _, _ = preprocess_image(image_path_watermarked)
    Y, _, _ = preprocess_image(image_path_origin)

    # 提取水印 LL
    extracted_watermark_ll = extract_watermark_ll(Y_watermarked, Y, alpha)
    extracted_watermark_ll = np.clip(extracted_watermark_ll, 0, 1).astype(np.uint8)  # 确保提取结果为二值
    #extracted_watermark = np.clip(extracted_watermark, 0, 255).astype(np.uint8)
    # 对所提取的水印，以 1 位 PNG 格式打包
    #cv2.imwrite('extracted_watermark.png', extracted_watermark)
    extracted_watermark_ll_img = Image.fromarray(extracted_watermark_ll * 255).convert("1")
    # TODO 显示在GUI上
    #extracted_watermark_img.save('extracted_watermark.png')

    # 提取水印 HL/LH
    extracted_watermark_hl = extract_watermark_hl(Y_watermarked, alpha)
    extracted_watermark_hl = np.clip(extracted_watermark_hl, 0, 1).astype(np.uint8)  # 确保提取结果为二值
    # 对所提取的水印，以 1 位 PNG 格式打包
    extracted_watermark_hl_img = Image.fromarray(extracted_watermark_hl * 255).convert("1")
    # TODO 显示在GUI上

#####################################################################################


