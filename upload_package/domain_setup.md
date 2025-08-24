# 域名配置检查清单

## 1. 域名购买后配置

### DNS解析记录配置
```
记录类型: A
主机记录: @
记录值: 你的服务器IP
TTL: 600

记录类型: A
主机记录: www  
记录值: 你的服务器IP
TTL: 600

记录类型: CNAME
主机记录: *
记录值: your-domain.com
TTL: 600
```

## 2. 服务器配置更新

### 更新.env文件
```bash
# 登录服务器后编辑
nano /var/www/workreport/.env

# 修改以下配置
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,server-ip
USE_HTTPS=true  # 如果配置了SSL
```

### 更新Nginx配置
```bash
# 编辑Nginx配置
nano /etc/nginx/sites-available/workreport

# 修改server_name
server_name your-domain.com www.your-domain.com;

# 重启Nginx
systemctl restart nginx
```

## 3. SSL证书配置

### 使用Let's Encrypt免费SSL
```bash
# 安装certbot
apt install certbot python3-certbot-nginx

# 获取SSL证书
certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 4. 测试检查

### 检查域名解析
```bash
# 检查A记录
nslookup your-domain.com

# 检查网站访问
curl -I http://your-domain.com
curl -I https://your-domain.com
```

### 在线检测工具
- DNS检查: https://dnschecker.org
- SSL检查: https://www.ssllabs.com/ssltest/
- 网站速度: https://gtmetrix.com

## 5. 备案后续

如果选择备案：
1. 备案期间网站不能访问
2. 备案成功后才能正式上线
3. 需要在网站底部添加备案号
4. 定期检查备案状态
