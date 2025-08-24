"""
Gunicorn配置文件
"""
import multiprocessing
import os

# 服务器绑定
bind = "127.0.0.1:8000"  # 内网地址，通过Nginx代理

# 工作进程数（建议CPU核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# 工作进程类型
worker_class = "sync"

# 每个工作进程的最大请求数
max_requests = 1000
max_requests_jitter = 100

# 超时设置
timeout = 120  # 请求超时时间
keepalive = 5  # 保持连接时间

# 预加载应用
preload_app = True

# 日志配置
accesslog = "/var/log/workreport/gunicorn_access.log"
errorlog = "/var/log/workreport/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程名称
proc_name = "workreport"

# 用户和组（安全设置）
user = "www-data"  # 根据你的系统调整
group = "www-data"

# PID文件
pidfile = "/var/run/workreport/gunicorn.pid"

# 临时目录
tmp_upload_dir = "/tmp"

# 启动时执行的操作
def on_starting(server):
    """服务器启动时执行"""
    server.log.info("正在启动WorkReport服务器...")

def on_reload(server):
    """重载时执行"""
    server.log.info("重新加载WorkReport服务器...")

def worker_int(worker):
    """工作进程中断时执行"""
    worker.log.info("工作进程 %s 被中断", worker.pid)

def pre_fork(server, worker):
    """工作进程创建前执行"""
    server.log.info("工作进程 %s 即将启动", worker.pid)

def post_fork(server, worker):
    """工作进程创建后执行"""
    server.log.info("工作进程 %s 已启动", worker.pid)
