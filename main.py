import sys
import os
from PyQt5.QtWidgets import QApplication

from modules.database import  db_utils
from modules.ui import gui
from modules.utils import utils

# 定义数据库路径
DB_FOLDER = "data"
DB_PATH = os.path.join(DB_FOLDER, "contacts.db")




# utils.log_action()



# 启动GUI
def main_gui():
    app = QApplication(sys.argv) #sys.argv 是一个列表，其中包含了运行 Python 脚本时传递的命令行参数
    window = gui.WatermarkApp()
    window.show()
    sys.exit(app.exec_())

# 数据库检测
#def main_db():
def test_database():
    print("开始测试数据库")
    conn = db_utils.init_db()
    print("数据库已连接")
    db_utils.create_tables(conn)
    print("数据库和表初始化完成")
    conn.close()

# 读取配置文件
def test_config():
    config = utils.load_config()

    # 读取数据
    database_directory = config['directories']['database_directory']
    image_to_process_directory = config['directories']['image_to_process_directory']
    image_source_directory = config['directories']['image_source_directory']
    image_watermarked_directory = config['directories']['image_watermarked_directory']
    log_mode = config.getboolean('settings', 'log')

    print(f"Database URL: {database_directory}")
    print(f"Image Directory 1: {image_to_process_directory}")
    print(f"Image Directory 2: {image_source_directory}")
    print(f"Image Directory 3: {image_watermarked_directory}")
    print(f"Log Mode: {log_mode}")


if __name__ == "__main__":
    test_config()
    test_database()
    main_gui()
