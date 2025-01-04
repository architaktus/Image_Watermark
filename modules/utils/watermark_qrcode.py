import qrcode
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
#import subprocess #zopflipng
from zopflipng import png_optimize
from modules import config
from modules.utils import utils

# 水印

# 生成、输出单色图像二维码
def generate_qr_code(content, box_size=10, border=4):
    """
    生成、输出单色图像二维码

    :param content: 二维码包含的文字或版权信息
    :param watermark_id: 名称
    :param box_size: 每个方格的大小（像素）
    :param border: 边框大小（格子数）
    """
    qr = qrcode.QRCode(
        version=1,  # 控制二维码的大小，1 是最小尺寸
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 容错级别 H: 30% 容错
        box_size=box_size,
        border=border,
    )
    qr.add_data(content)
    qr.make(fit=True)

    # 将二维码转为图片
    qr_img = qr.make_image(fill_color="black", back_color="white") 
    qr_img = qr_img.convert("1")  # 转为单色 (1-bit)。1 表示单色图像

    return qr_img


# 调用
#content = "版权所有: Example Corp.\n授权时间: 2025-01-02\n唯一ID: 123456"
#generate_qr_code(content)


# 保存图像
def save_watermark_png(watermark_img, watermark_id):
    """
    将输入的图片保存为 PNG 格式。更新当前使用的水印

    :param watermark_img: 待输入的图片
    :param watermark_id: 水印id
    """
    # 生成地址
    qr_file_name = f"{watermark_id}.png"
    output_path = os.path.join(config.QRCODE_DIR, qr_file_name)
    #output_path_temp = output_path.replace(".png", "_temp.png")

    print(f"优化PNG")
    # 将 PIL Image 转换为字节流
    image_bytes = BytesIO()
    watermark_img.save(image_bytes, format="PNG")
    image_bytes = image_bytes.getvalue()  # 获取 PNG 格式的字节数据

    # 使用 png_optimize 压缩
    watermark_img_optimized, zustand = png_optimize(
        image_bytes,
        lossy_8bit=True,
        lossy_transparent=True,
        filter_strategies='01234mepb',
        num_iterations=50,
    )

    # 保存图片
    if zustand == 0:
        # 将优化后的 PNG 保存到文件
        with open(output_path, "wb") as f:
            f.write(watermark_img_optimized)    
            f.close()
    else:
        # 优化失败时
        print(f"zopfli优化失败 未优化的二维码已保存到: {output_path}")
        watermark_img.save(output_path, format="PNG", optimize=True, compress_level=9)


    print(f"二维码已成功保存于: {output_path}")

    # 更新全局配置
    utils.update_runtime_config(watermark_id, qr_file_name)