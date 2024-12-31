import sys
import os
from PyQt5.QtWidgets import QApplication
from modules.database import db_utils
from modules.ui import gui
from modules.utils import utils

# 定义数据库路径
DB_FOLDER = "data"
DB_PATH = os.path.join(DB_FOLDER, "contacts.db")




# utils.log_action()



# 启动GUI
def main():
    app = QApplication(sys.argv) #sys.argv 是一个列表，其中包含了运行 Python 脚本时传递的命令行参数
    window = gui.WatermarkApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()