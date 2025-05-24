import os
from multiprocessing import cpu_count

# 创建日志目录
LOG_DIR = "./gunicorn_log/"
os.makedirs(LOG_DIR, exist_ok=True)  # exist_ok=True 确保目录存在时不报错

# 基础配置
bind = "0.0.0.0:8000"
workers = cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# 性能优化
timeout = 60
keepalive = 15
max_requests = 1000
max_requests_jitter = 50

# 日志配置
accesslog = os.path.join(LOG_DIR, "gunicorn_access.log")
errorlog = os.path.join(LOG_DIR, "gunicorn_error.log")
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 调试配置
reload = os.environ.get("ENV") == "dev"