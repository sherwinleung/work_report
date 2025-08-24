# SCP上传和部署命令序列

## 🚀 本地操作（在你的Mac上）

### 1. 上传文件到服务器
```bash
# 替换 YOUR_SERVER_IP 为你的实际服务器IP
scp -r upload_package root@YOUR_SERVER_IP:/tmp/workreport

# 如果SSH端口不是22，使用：
# scp -P 端口号 -r upload_package root@YOUR_SERVER_IP:/tmp/workreport
```

### 2. 验证上传成功
```bash
# SSH连接到服务器
ssh root@YOUR_SERVER_IP

# 检查文件是否上传成功
ls -la /tmp/workreport
```

## 🔧 服务器操作（SSH连接后）

### 3. 移动文件到正确位置
```bash
# 创建项目目录
mkdir -p /var/www/workreport

# 移动文件
mv /tmp/workreport/* /var/www/workreport/

# 设置权限
chown -R www-data:www-data /var/www/workreport
```

### 4. 运行部署脚本
```bash
# 进入项目目录
cd /var/www/workreport

# 给脚本执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

### 5. 配置环境变量
```bash
# 复制环境配置模板
cp env.production.example .env

# 编辑配置文件
nano .env

# 需要修改的关键配置：
# DEBUG=False
# SECRET_KEY=your-super-secret-key-here
# ALLOWED_HOSTS=你的服务器IP,localhost
# DB_PASSWORD=你设置的MySQL密码
```

### 6. 完成部署
```bash
# 重启服务
systemctl restart nginx supervisor

# 检查服务状态
systemctl status nginx
systemctl status supervisor

# 测试访问
curl http://localhost
```

## 🧪 测试部署结果

### 浏览器测试
```
访问: http://你的服务器IP
应该看到: WorkReport登录页面
```

### 命令行测试
```bash
# 检查网站响应
curl -I http://你的服务器IP

# 检查各项服务
systemctl status mysql
systemctl status redis-server
systemctl status nginx
systemctl status supervisor
```

## ❗ 常见问题解决

### 上传失败
- 检查SSH连接是否正常
- 确认防火墙22端口已开放
- 验证服务器IP地址正确

### 部署脚本失败
- 检查网络连接
- 确认系统更新完成
- 查看错误日志：tail -f /var/log/syslog

### 服务无法启动
- 检查配置文件语法
- 查看服务日志
- 验证端口占用情况
