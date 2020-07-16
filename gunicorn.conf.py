# debug = True
loglevel = 'debug'
pidfile = "log/gunicorn.pid"  # 当前gunicorn允许的额pid
accesslog = "log/access.log"  # 登录记
errorlog = "log/debug.log"  # 错误日志

workers = 5  # 定义同时开启的处理请求的进程数量，根据网站流量适当调整
worker_class = "gevent"  # 采用gevent库，支持异步处理请求，提高吞吐量
bind = "0.0.0.0:80"  # 帮顶端口
