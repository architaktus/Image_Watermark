import sqlite3
import os
# SQL 不支持像 Python 那样用 # 作为注释符号。SQLite 使用双连字符 (--) 或 /* ... */ 来添加注释。


# 初始化数据库连接并返回连接对象
def init_db(db_name="project.db"):
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
            image_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            filename_original    TEXT,        -- 文件名
            filename_new    TEXT,        -- 新文件名
            iptc_original  TEXT,        -- JSON或字符串形式存储 IPTC
            iptc_new  TEXT,        -- JSON或字符串形式存储 IPTC
            exif_info_original   TEXT,        -- JSON或字符串形式存储Exif  SELECT json_extract(exif_info_original, '$.camera_model') FROM image_info;
            exif_info_new   TEXT        -- JSON或字符串形式存储Exif            
        )
    ''')

    # watermark_info 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watermark_info (
            watermark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id     INTEGER,    -- 关联 image_info 表
            create_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
            watermark_content     TEXT,       -- 完整水印信息("©2024 Name...")
            watermark_encrypted     TEXT,       -- 加密水印文本
            watermark_key     TEXT,       -- 加密水印密钥
            watermark_random_key     TEXT,       -- 伪随机数密钥
            watermark_random     TEXT,       -- 伪随机数
            /** location     TEXT,       -- 图片中嵌入水印的位置("LL子带"、"DCT中频"等) **/
            FOREIGN KEY (image_id) REFERENCES image_info (image_id)       -- 外键关系: watermark 表中的 image_id 字段与 image 表中的 image_id 字段相关联
        )
    ''')

    # watermark 水印图 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watermark_img (
            watermark_id INTEGER,    -- 关联watermark_info表
            image_id     INTEGER,    -- 关联image_info表
            FOREIGN KEY (image_id) REFERENCES image_info (image_id)       -- 外键关系: image_id 字段与 image 表中的 image_id 字段相关联
            FOREIGN KEY (watermark_id) REFERENCES watermark_info (watermark_id)       -- 外键关系: image_id 字段与 watermark_info 表中的 watermark_id 字段相关联
        )
    ''')

    # cursor.execute("PRAGMA table_info('image_info');")
    # columns = cursor.fetchall()
    # print("Columns in image_info:", columns)

    conn.commit()



#######################################################################################################################################
#######################################################################################################################################
# 插入和查询操作

