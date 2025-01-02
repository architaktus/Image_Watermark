import os
import json
from PIL import Image, ExifTags
import pyexiv2

#######################################################################################################################################
#######################################################################################################################################

# 检查 to_process 文件夹
def get_image_list(folder_path, extensions=(".jpg", ".png", ".jpeg", ".gif")):
    """
    获取指定文件夹中的图片文件列表。
    
    :param folder_path: 要检查的文件夹路径
    :param extensions: 支持的文件扩展名
    :return: 图片文件名列表
    """
    if not os.path.exists(folder_path):
        return []
    
    return [file for file in os.listdir(folder_path) if file.lower().endswith(extensions)]


#######################################################################################################################################
#######################################################################################################################################
# 选取图片，读取信息
def read_image(image_path):
    """
    读取选中图片的信息
    """
    metadata = extract_metadata(image_path)
    #print(f"Processing image: {image_path}")
    #print(f"title/format/mode/size = {metadata['title']} & {metadata['format']} & {metadata['mode']} & {metadata['size']['width']} x {metadata['size']['height']}")
    #print(f"compression = {metadata['compression']}")
    #print(f"exif = {metadata['exif']}")
    #print(f"iptc = {metadata['iptc']}")


    
# 提取图片元数据
# TODO .gif相关
def extract_metadata(image_path):
    """
    提取图片的元数据————包括标题等基础信息、EXIF 和 IPTC 信息。

    :param image_path: 图片文件的路径
    :return: 包含元数据的多层级字典
    """
    metadata = {
        'title': "",
        'format': "",
        'mode': "",
        'size': {
            'width': "",
            'height': ""
        },
        'compression': {},  #json.dumps({}),
        'exif': {}, #json.dumps({}),  # 初始化为空 JSON 字符串 TODO 按确认按钮后转写json
        'iptc': {} #json.dumps({})
    }
    # 使用 Pillow 提取标题等基础数据
    try:
        with Image.open(image_path) as img:
            metadata['title'] = os.path.basename(img.filename)
            metadata['format'] = img.format  # 文件格式
            metadata['mode'] = img.mode      # 图像模式
            metadata['size']['width'] = img.size[0]  # 尺寸 (宽)
            metadata['size']['height'] = img.size[1]  # 尺寸 (高)

            # JPEG
            if img.format == "JPEG":
                metadata['compression']['compression_format'] = "JPEG"
                metadata['compression']['quality'] = img.info.get('quality', '')  # 获取质量设置
                metadata['compression']['subsampling'] = img.info.get('subsampling', '')  # 子采样
                metadata['compression']['dpi'] = img.info.get('dpi', '')  # DPI 信息
            # PNG
            elif img.format == "PNG":
                metadata['compression']['compression_format'] = "PNG-ZIP"
                metadata['compression']['compress_level'] = img.info.get('compress_level', '')  # 压缩级别
                metadata['compression']['dpi'] = img.info.get('dpi', '')  # DPI 信息
            else:
                pass
    except Exception:
        pass


    # 提取 EXIF 信息
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                #exif_dict = {}
                for tag_id, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                    metadata['exif'][tag_name] = value
                #metadata['exif'] = json.dumps(exif_dict)  # 仅存储成功提取的 EXIF 数据
    except Exception:
        pass  # 跳过错误
            #else:
                #metadata['exif'] = {}
                #print(f"No EXIF data found")          
#    except Exception as e:
#        metadata['exif'] = {}
        #f"Error reading EXIF: {e}"
        #print(f"Error reading EXIF: {e}")
    #print(metadata['exif']) 
    
    # 使用 pyexiv2 提取 IPTC 信息
    try:
        with pyexiv2.Image(image_path) as meta_img:
            iptc_data = meta_img.read_iptc()
            if iptc_data:
                metadata['iptc'] = iptc_data
                #metadata['iptc'] = json.dumps(iptc_data)  # 仅存储成功提取的 IPTC 数据
    except (ModuleNotFoundError, Exception):
        pass  # 跳过错误
#    except ModuleNotFoundError:
#        metadata['iptc'] = {}
        #"pyexiv2 module not found"
        #print(f"pyexiv2 module not found")
#    except Exception as e:
#        metadata['iptc'] = {}
        #f"Error reading IPTC: {e}" 
        #print(f"Error reading IPTC: {e}" )
    #print(metadata['iptc']) 
    
    return metadata


# 更新版权信息
def update_copyright(image_path, copyright_info):
    try:
        with pyexiv2.Image(image_path) as img:
            img.modify_exif({'Exif.Image.Copyright': copyright_info})
            img.write()
    except Exception as e:
        print(f"Error updating EXIF: {e}")