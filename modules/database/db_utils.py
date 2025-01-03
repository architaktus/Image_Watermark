import sqlite3
import os
from modules import config
from modules.utils import utils
from modules.utils import watermark_qrcode
# SQL 不支持像 Python 那样用 # 作为注释符号。SQLite 使用双连字符 (--) 或 /* ... */ 来添加注释。


# 初始化数据库连接并返回连接对象
def init_db(db_name="watermark.db"):
    """
    初始化数据库连接、创建数据文件夹、检测版权信息更新情况等。
    """
    # 确保数据库路径指向 data 文件夹
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data")
    os.makedirs(data_dir, exist_ok=True)  # 如果 data 文件夹不存在，自动创建
    db_path = os.path.join(data_dir, db_name)
    conn = sqlite3.connect(db_path)

    return conn

# 创建表
def create_tables(conn):
    cursor = conn.cursor()

   # image_info 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id    TEXT,               -- 图片id
            filename_original    TEXT,        -- 文件名
            filename_new    TEXT,        -- 新文件名
            iptc_original  TEXT,        -- JSON或字符串形式存储 IPTC
            iptc_new  TEXT,        -- JSON或字符串形式存储 IPTC
            exif_info_original   TEXT,        -- JSON或字符串形式存储Exif  SELECT json_extract(exif_info_original, '$.camera_model') FROM image_info;
            exif_info_new   TEXT        -- JSON或字符串形式存储Exif
        )
    ''')

    # watermark_info 表,记录每张图片的水印数据
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watermark_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 自增主键
            watermark_id TEXT,       -- 水印id
            image_id     INTEGER,       -- 关联 image_info 表
            create_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
            alpha_ll    REAL,       -- NUMERIC 用于频带计算的alpha值————LL频带
            alpha_lh_hl REAL,       -- NUMERIC 用于频带计算的alpha值————LH和HL频带
            FOREIGN KEY (image_id) REFERENCES image_info (image_id)       -- 外键关系: watermark 表中的 image_id 字段与 image 表中的 image_id 字段相关联
        )
    ''')

    # watermark 表，记录qrcode相关信息
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watermark (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- 自增主键
            watermark_id TEXT NOT NULL UNIQUE,       -- 水印id
            image_ids     TEXT,       -- 使用此水印的图片
            watermark_content     TEXT NOT NULL UNIQUE,       -- 简短水印信息("©Name 2024")
            watermark_file_name     TEXT NOT NULL,       -- 水印图片名称
            FOREIGN KEY (watermark_id) REFERENCES watermark_info (watermark_id)       -- 外键关系: watermark 表中的 watermark_id 字段与 watermark_info 表中的 watermark_id 字段相关联
        )
    ''')

    # cursor.execute("PRAGMA table_info('image_info');")
    # columns = cursor.fetchall()
    # print("Columns in image_info:", columns)

    conn.commit()



#######################################################################################################################################
#######################################################################################################################################
# 插入和查询操作


# 检查水印内容是否存在
def check_or_create_watermark(conn, content):
    """
    检测水印内容是否已存在，存在则返回 ID 、不存在则创建新条目和二维码。
    """
    # 查询是否已有相同内容
    cursor = conn.cursor()
    cursor.execute("SELECT id, watermark_id, watermark_file_name FROM watermark WHERE watermark_content = ?", (content,))
    result = cursor.fetchone()

    if result:
    # 如果内容已存在
        exist_qr_dir = os.path.join(config.QRCODE_DIR, result[2])
        if utils.check_file_exists(exist_qr_dir):
            print(f"水印已存在: ID = {result[0]}, 文件路径 = {exist_qr_dir}")
            return utils.update_runtime_config(result[1], result[2])    # 更新水印信息
        
        # 存在于数据库但未能找到水印图————生成新水印图
        qr_img = watermark_qrcode.generate_qr_code(content)
        watermark_qrcode.save_watermark_png(qr_img, result[1])
        print(f"数据库检索成功，水印文件搜索失败，新水印已自动创建: ID = {result[1]}, 文件路径 = {config.runtime_config['WM_FILE_DIR']}")
    # 内容不存在，生成新水印id
    else:
        watermark_id = get_next_watermark_id(conn)

            # 生成新水印图
        qr_img = watermark_qrcode.generate_qr_code(content)
        watermark_qrcode.save_watermark_png(qr_img, watermark_id)    
        print(f"新水印已创建: ID = {watermark_id}")

            # 插入新记录到数据库
        qr_title = config.runtime_config['WM_FILE_NAME']
        save_watermark_record(conn, watermark_id, content,qr_title )



################################################################
# 生成 watermark_id
def get_next_watermark_id(conn):
    """
    获取新 watermark_id
    """
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM watermark_info")
    next_id = cursor.fetchone()[0]
    return f"WM{next_id:06d}"  # 格式化为 WM000001, WM000002 等


################################################################
# 将记录插入数据库
def save_watermark_record(conn, watermark_id, content, file_name):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO watermark (watermark_id, watermark_content, watermark_file_name)
        VALUES (?, ?, ?)
    ''', (watermark_id, content, file_name))
    conn.commit()
    print(f"数据库watermark表格 新条目已创建")
