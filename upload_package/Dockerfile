# WorkReport Docker镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=workreport.settings_production

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements_production.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements_production.txt

# 复制项目文件
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# 启动命令
CMD ["gunicorn", "--config", "gunicorn.conf.py", "workreport.wsgi:application"]
