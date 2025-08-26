# WorkReport 阿里云部署指南

## 🚀 部署概述

本指南提供了两种部署方案：
1. **传统部署** - 使用Nginx + Gunicorn + Supervisor
2. **Docker部署** - 使用Docker Compose（推荐）

## 📋 准备工作

### 1. 阿里云服务器配置
- **规格建议**: 2核4G内存，40G系统盘
- **操作系统**: Ubuntu 20.04 LTS
- **网络**: 配置安全组开放80、443、22端口

### 2. 域名配置
- 在阿里云域名控制台配置A记录指向服务器IP
- 如需要：配置www子域名

### 3. 必需的账号和密钥
- 数据库密码
- Django SECRET_KEY
- API密钥（OpenAI/DeepSeek等）
- 邮箱配置（用于错误通知）

## 🔧 方案一：传统部署

### 1. 连接服务器
```bash
ssh root@your-server-ip
```

### 2. 上传代码
```bash
# 方法1：Git克隆
git clone https://github.com/sherwinleung/work_report.git
cd work_report

# 方法2：SCP上传
scp -r /path/to/local/project root@server-ip:/var/www/workreport
```

### 3. 运行部署脚本
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. 配置环境变量
```bash
# 编辑配置文件
nano /var/www/workreport/.env

# 必须修改的配置：
DEBUG=False
SECRET_KEY=你的密钥
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,server-ip
DB_PASSWORD=数据库密码

# API密钥配置
DEFAULT_OPENAI_API_KEY=sk-QLZDJaU1a8uuoYfdaN52FPzpoFFUmPlhEOmgmyMZ5g=
DEFAULT_DEEPSEEK_API_KEY=sk-d40ba7f7a4b242268876d3ca27d72684
```

### 5. 配置域名
```bash
# 编辑Nginx配置
nano /etc/nginx/sites-available/workreport

# 修改server_name
server_name your-domain.com www.your-domain.com;
```

### 6. 重启服务
```bash
systemctl restart nginx supervisor
```

### 7. 配置SSL证书（推荐）
```bash
# 安装certbot
apt install certbot python3-certbot-nginx

# 获取SSL证书
certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🐳 方案二：Docker部署（推荐）

### 1. 安装Docker和Docker Compose
```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### 2. 准备配置文件
```bash
# 复制环境配置
cp env.production.example .env

# 编辑配置
nano .env
```

### 3. 启动服务
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f web
```

### 4. 初始化数据库
```bash
# 运行数据库迁移
docker-compose exec web python manage.py migrate

# 创建超级用户
docker-compose exec web python manage.py createsuperuser

# 初始化默认API配置
docker-compose exec web python manage.py init_default_apis
```

## 📊 监控和维护

### 1. 日志查看
```bash
# 传统部署
tail -f /var/log/workreport/django.log
tail -f /var/log/nginx/workreport_access.log

# Docker部署
docker-compose logs -f web
docker-compose logs -f nginx
```

### 2. 服务状态检查
```bash
# 传统部署
systemctl status nginx supervisor mysql redis-server

# Docker部署
docker-compose ps
```

### 3. 备份数据库
```bash
# 传统部署
mysqldump -u workreport_user -p workreport > backup_$(date +%Y%m%d).sql

# Docker部署
docker-compose exec db mysqldump -u workreport_user -p workreport > backup_$(date +%Y%m%d).sql
```

### 4. 更新应用
```bash
# 传统部署
cd /var/www/workreport
git pull origin main
source venv/bin/activate
pip install -r requirements_production.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart supervisor

# Docker部署
git pull origin main
docker-compose build web
docker-compose up -d web
```

## 🔒 安全建议

### 1. 服务器安全
- 禁用root登录，使用密钥认证
- 配置防火墙只开放必要端口
- 定期更新系统和软件包
- 使用fail2ban防止暴力破解

### 2. 应用安全
- 使用强密码和复杂的SECRET_KEY
- 启用HTTPS
- 定期备份数据
- 监控日志文件

### 3. 数据库安全
- 使用复杂密码
- 限制数据库访问权限
- 定期备份数据库

## 🔧 故障排除

### 1. 常见问题

**502 Bad Gateway**
```bash
# 检查Gunicorn是否运行
systemctl status supervisor
# 或
docker-compose logs web
```

**静态文件404**
```bash
# 重新收集静态文件
python manage.py collectstatic --noinput
```

**数据库连接错误**
```bash
# 检查数据库服务
systemctl status mysql
# 或
docker-compose logs db
```

### 2. 性能优化

**增加工作进程数**
```python
# 编辑gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1
```

**启用Nginx缓存**
```nginx
# 在nginx.conf中添加
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 📞 技术支持

如遇到问题，请检查：
1. 服务器日志文件
2. Nginx错误日志
3. Django应用日志
4. 数据库连接状态

更多问题请参考Django官方部署文档或联系技术支持。
