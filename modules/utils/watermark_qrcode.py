from PIL import Image, ImageDraw, ImageFont

# 水印
def embed_text_watermark(input_path, output_path, text, position=(10,10)):
    img = Image.open(input_path)
    draw = ImageDraw.Draw(img)
    # 如果要使用本地字体文件，如 Windows 的 "msyh.ttc"
    font = ImageFont.truetype("arial.ttf", 30)  
    draw.text(position, text, font=font, fill=(255,255,255,128))  # RGBA
    img.save(output_path, quality=95)