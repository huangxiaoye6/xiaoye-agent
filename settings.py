# aerich init -t settings.py.orm
# aerich init-db
# aerich migrate
# aerich upgrade
# 配置数据库连接
from dotenv import load_dotenv
import os
load_dotenv()
orm={
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": os.getenv("DB_HOST", "127.0.0.1"),
                "port": int(os.getenv("DB_PORT", 3306)),
                "user": os.getenv("DB_USER", "root"),
                "password": os.getenv("DB_PASSWORD"),
                "database":os.getenv("DB_NAME","agent"),
            }
        }
    },
    "apps": {
        "models": {
            "models": ["models.UserModel","aerich.models"],
            "default_connection": "default",
        }
    },
    "use_tz":False,
    "timezone": "Asia/Shanghai",  # 配置时区
}

SECRET_KEY='x$&1hc4z7jau@6d8ii(kx(c7l8kmc^$i4xoqb4x-lxr-n4'

success_code=1000  # 成功状态码
creat_error_code=1001  # 创建失败状态码
search_error_code=1002 # 查询失败
error_code=2000 # 普通失败状态码
ai_agent_error=4001 # 智能体响应失败


# 邮箱配置
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')