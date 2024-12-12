# 导入multiprocessing模块
import multiprocessing

# 绑定地址和端口
bind = "0.0.0.0:42110"
# 工作进程数
workers = 2
# 工作进程类
worker_class = "uvicorn.workers.UvicornWorker"
# 超时时间
timeout = 120
# 保持连接时间
keep_alive = 60
# 访问日志文件
accesslog = "-"
# 错误日志文件
errorlog = "-"
# 日志级别
loglevel = "debug"
