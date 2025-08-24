#!/bin/bash

# WorkReport阿里云部署脚本
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 项目配置
PROJECT_NAME="workreport"
PROJECT_USER="www-data"
PROJECT_PATH="/var/www/workreport"
VENV_PATH="/var/www/workreport/venv"
REPO_URL="https://github.com/sherwinleung/work_report.git"  # 替换为你的仓库地址

# 检查是否以root身份运行
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要以root身份运行"
        exit 1
    fi
}

# 更新系统
update_system() {
    log_info "更新系统包..."
    apt update && apt upgrade -y
    log_success "系统更新完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装系统依赖..."
    apt install -y python3 python3-pip python3-venv python3-dev \
                   nginx mysql-server redis-server \
                   git curl wget unzip \
                   libmysqlclient-dev pkg-config \
                   supervisor htop nano
    log_success "系统依赖安装完成"
}

# 配置MySQL
setup_mysql() {
    log_info "配置MySQL数据库..."
    
    # 启动MySQL服务
    systemctl start mysql
    systemctl enable mysql
    
    # 创建数据库和用户
    mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS workreport CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'workreport_user'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON workreport.* TO 'workreport_user'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    log_success "MySQL配置完成"
    log_warning "请记住数据库密码: your_password_here"
}

# 配置Redis
setup_redis() {
    log_info "配置Redis..."
    systemctl start redis-server
    systemctl enable redis-server
    log_success "Redis配置完成"
}

# 创建项目用户和目录
setup_project_structure() {
    log_info "创建项目结构..."
    
    # 创建项目目录
    mkdir -p $PROJECT_PATH
    mkdir -p /var/log/workreport
    mkdir -p /var/run/workreport
    
    # 设置权限
    chown -R $PROJECT_USER:$PROJECT_USER $PROJECT_PATH
    chown -R $PROJECT_USER:$PROJECT_USER /var/log/workreport
    chown -R $PROJECT_USER:$PROJECT_USER /var/run/workreport
    
    log_success "项目结构创建完成"
}

# 部署代码
deploy_code() {
    log_info "部署应用代码..."
    
    # 切换到项目用户
    sudo -u $PROJECT_USER bash <<EOF
cd $PROJECT_PATH

# 克隆或更新代码
if [ -d ".git" ]; then
    git pull origin main
else
    git clone $REPO_URL .
fi

# 创建虚拟环境
python3 -m venv $VENV_PATH
source $VENV_PATH/bin/activate

# 安装Python依赖
pip install --upgrade pip
pip install -r requirements_production.txt

# 复制配置文件
cp env.production.example .env

# 创建日志目录
mkdir -p logs

# 收集静态文件
export DJANGO_SETTINGS_MODULE=workreport.settings_production
python manage.py collectstatic --noinput

# 运行数据库迁移
python manage.py migrate

# 创建超级用户（可选）
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='564999607@qq.com').exists() or User.objects.create_superuser('564999607@qq.com', '564999607@qq.com', 'admin123')" | python manage.py shell

# 初始化默认API配置
python manage.py init_default_apis
EOF
    
    log_success "代码部署完成"
}

# 配置Supervisor
setup_supervisor() {
    log_info "配置Supervisor..."
    
    cat > /etc/supervisor/conf.d/workreport.conf <<EOF
[program:workreport]
command=$VENV_PATH/bin/gunicorn -c $PROJECT_PATH/gunicorn.conf.py workreport.wsgi:application
directory=$PROJECT_PATH
user=$PROJECT_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/workreport/supervisor.log
environment=DJANGO_SETTINGS_MODULE=workreport.settings_production
EOF
    
    # 重启Supervisor
    systemctl restart supervisor
    systemctl enable supervisor
    
    log_success "Supervisor配置完成"
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
    # 复制配置文件
    cp $PROJECT_PATH/nginx.conf /etc/nginx/sites-available/workreport
    
    # 更新配置文件中的路径
    sed -i "s|/path/to/your/project|$PROJECT_PATH|g" /etc/nginx/sites-available/workreport
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/workreport /etc/nginx/sites-enabled/
    
    # 删除默认站点
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    nginx -t
    
    # 重启Nginx
    systemctl restart nginx
    systemctl enable nginx
    
    log_success "Nginx配置完成"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    ufw allow 22/tcp   # SSH
    ufw allow 80/tcp   # HTTP
    ufw allow 443/tcp  # HTTPS
    ufw --force enable
    
    log_success "防火墙配置完成"
}

# 创建SSL证书（Let's Encrypt）
setup_ssl() {
    log_info "设置SSL证书 (Let's Encrypt)..."
    
    # 安装certbot
    apt install -y certbot python3-certbot-nginx
    
    log_warning "SSL证书设置需要手动完成"
    log_info "请运行: certbot --nginx -d your-domain.com -d www.your-domain.com"
}

# 主函数
main() {
    log_info "开始部署WorkReport到阿里云..."
    
    check_root
    update_system
    install_dependencies
    setup_mysql
    setup_redis
    setup_project_structure
    deploy_code
    setup_supervisor
    setup_nginx
    setup_firewall
    
    log_success "🎉 WorkReport部署完成！"
    log_info "接下来的步骤:"
    log_info "1. 编辑 $PROJECT_PATH/.env 文件，配置你的域名和密钥"
    log_info "2. 编辑 /etc/nginx/sites-available/workreport，设置你的域名"
    log_info "3. 重启服务: systemctl restart nginx supervisor"
    log_info "4. 如需SSL证书，运行: certbot --nginx -d your-domain.com"
    log_info "5. 访问你的网站进行测试"
}

# 运行主函数
main "$@"
