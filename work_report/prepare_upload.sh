#!/bin/bash

# 准备上传脚本 - 清理不需要的文件

echo "🧹 准备WorkReport项目文件上传..."

# 创建上传目录
mkdir -p upload_package

# 复制需要的文件到上传目录
echo "📦 复制项目文件..."

# 复制应用代码
cp -r apps/ upload_package/
cp -r templates/ upload_package/
cp -r static/ upload_package/
cp -r workreport/ upload_package/

# 复制配置文件
cp manage.py upload_package/
cp requirements*.txt upload_package/
cp gunicorn.conf.py upload_package/
cp nginx.conf upload_package/
cp deploy.sh upload_package/
cp env.production.example upload_package/
cp Dockerfile upload_package/
cp docker-compose.yml upload_package/
cp DEPLOYMENT.md upload_package/

# 复制文档
cp *.md upload_package/ 2>/dev/null || true

echo "✅ 文件准备完成"
echo "📋 上传包内容:"
ls -la upload_package/

echo ""
echo "🚀 接下来运行上传命令:"
echo "scp -r upload_package root@YOUR_SERVER_IP:/tmp/workreport"
