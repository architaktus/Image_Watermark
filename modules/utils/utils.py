import os
from configparser import ConfigParser



# 操作日志/记录
def log_action(db_conn, action_type, description):
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO logs (action_type, description) VALUES (?, ?)", (action_type, description))
    db_conn.commit()

#######################################################################################################################################
#######################################################################################################################################
# 加载配置 #############################################################################################################################

# 配置文件路径
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) # 项目根目录
CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'config.ini')

# 缓存配置对象
_config = None

def load_config():
    global _config
    if _config is None:  # 仅第一次调用时加载配置
        # 创建配置解析器实例
        config = ConfigParser()
        if not os.path.exists(CONFIG_FILE):
            raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")
        # 读取配置文件 
        config.read(CONFIG_FILE)
        _config = config
    return _config


