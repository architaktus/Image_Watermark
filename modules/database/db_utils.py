import sqlite3

# SQL 不支持像 Python 那样用 # 作为注释符号。SQLite 使用双连字符 (--) 或 /* ... */ 来添加注释。
def initialize_database():
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
   # 创建 image 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image (
            image_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT,        -- 文件名
            resolution  TEXT,        -- 分辨率，如 "2500x2500"
            exif_info   TEXT,        -- JSON或字符串形式存储Exif
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建 watermark 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watermark (
            watermark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id     INTEGER,    -- 关联image表
            type         TEXT,       -- watermark类型(关键信息/辅助/隐蔽等)
            content      TEXT,       -- 水印内容("©2024 Name")
            location     TEXT,       -- 图片中嵌入水印的位置("LL子带"、"DCT中频"等)
            key_info     TEXT,       -- 密钥或加密信息
            create_time  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES image (image_id)       -- watermark 表中的 image_id 字段与 image 表中的 image_id 字段相关联
        )
    ''')

    conn.commit()
    conn.close()