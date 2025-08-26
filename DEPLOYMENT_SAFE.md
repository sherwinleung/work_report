# 阿里云项目安全部署流程

## 📋 部署前检查清单

### 1. 数据备份（必须执行）
```bash
# 1.1 创建备份目录
mkdir -p /opt/backups/$(date +%Y%m%d_%H%M%S)

# 1.2 备份数据库
cp /opt/work_report/db.sqlite3 /opt/backups/$(date +%Y%m%d_%H%M%S)/db.sqlite3.backup

# 1.3 备份用户上传文件（如果有）
cp -r /opt/work_report/media /opt/backups/$(date +%Y%m%d_%H%M%S)/media_backup 2>/dev/null || echo "No media files"

# 1.4 备份配置文件
cp /opt/work_report/.env /opt/backups/$(date +%Y%m%d_%H%M%S)/.env.backup 2>/dev/null || echo "No .env file"

# 1.5 验证备份
ls -la /opt/backups/$(date +%Y%m%d_%H%M%S)/
```

### 2. 服务状态检查
```bash
# 2.1 检查当前服务状态
supervisorctl status workreport
systemctl status nginx

# 2.2 检查数据库连接
cd /opt/work_report
source venv/bin/activate
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py check

# 2.3 记录当前用户数据量
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.worklog.models import WorkEntry
from apps.reports.models import Report
User = get_user_model()
print(f'部署前数据: Users={User.objects.count()}, WorkEntries={WorkEntry.objects.count()}, Reports={Report.objects.count()}')
"
```

## 🚀 安全部署流程

### 方法1: 增量更新（推荐）
```bash
# 1. 停止服务
supervisorctl stop workreport

# 2. 进入项目目录
cd /opt/work_report

# 3. 拉取最新代码（保持数据文件）
git stash  # 暂存本地修改
git pull origin main
git stash pop  # 恢复本地修改

# 4. 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 5. 运行迁移（不会删除数据）
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py makemigrations
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py migrate

# 6. 收集静态文件
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py collectstatic --noinput

# 7. 重启服务
supervisorctl start workreport
supervisorctl status workreport

# 8. 验证数据完整性
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.worklog.models import WorkEntry
from apps.reports.models import Report
User = get_user_model()
print(f'部署后数据: Users={User.objects.count()}, WorkEntries={WorkEntry.objects.count()}, Reports={Report.objects.count()}')
"
```

### 方法2: 完整替换（高风险，需谨慎）
```bash
# 1. 完整备份（必须）
BACKUP_DIR="/opt/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp -r /opt/work_report $BACKUP_DIR/work_report_backup

# 2. 停止服务
supervisorctl stop workreport

# 3. 保护数据文件
mv /opt/work_report/db.sqlite3 /tmp/db.sqlite3.preserve
mv /opt/work_report/.env /tmp/.env.preserve 2>/dev/null || echo "No .env to preserve"
mv /opt/work_report/media /tmp/media.preserve 2>/dev/null || echo "No media to preserve"

# 4. 上传新代码
cd /opt
tar -xzf workreport_latest.tar.gz
chown -R www-data:www-data work_report

# 5. 恢复数据文件
mv /tmp/db.sqlite3.preserve /opt/work_report/db.sqlite3
mv /tmp/.env.preserve /opt/work_report/.env 2>/dev/null || echo "No .env to restore"
mv /tmp/media.preserve /opt/work_report/media 2>/dev/null || echo "No media to restore"

# 6. 设置权限
chown www-data:www-data /opt/work_report/db.sqlite3
chmod 664 /opt/work_report/db.sqlite3

# 7. 更新环境
cd /opt/work_report
source venv/bin/activate
pip install -r requirements.txt

# 8. 运行迁移
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py migrate

# 9. 收集静态文件
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py collectstatic --noinput

# 10. 重启服务
supervisorctl start workreport

# 11. 验证数据完整性
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.worklog.models import WorkEntry
from apps.reports.models import Report
User = get_user_model()
print(f'部署后数据: Users={User.objects.count()}, WorkEntries={WorkEntry.objects.count()}, Reports={Report.objects.count()}')
"
```

## 🛡️ 数据保护最佳实践

### 1. 定期备份
```bash
# 创建定期备份脚本
cat > /opt/scripts/backup_workreport.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/work_report/db.sqlite3 $BACKUP_DIR/db.sqlite3
gzip $BACKUP_DIR/db.sqlite3

# 备份配置
cp /opt/work_report/.env $BACKUP_DIR/ 2>/dev/null || true

# 清理30天前的备份
find /opt/backups -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x /opt/scripts/backup_workreport.sh

# 设置每日备份 (添加到crontab)
echo "0 2 * * * /opt/scripts/backup_workreport.sh" | crontab -
```

### 2. 数据库迁移安全检查
```bash
# 迁移前检查
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py showmigrations

# 模拟迁移（dry-run）
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py migrate --plan

# 只有确认安全后才执行真正的迁移
DJANGO_SETTINGS_MODULE=workreport.settings_production python3 manage.py migrate
```

### 3. 回滚计划
```bash
# 如果部署失败，快速回滚
BACKUP_DIR="/opt/backups/20250824_103000"  # 使用实际备份目录

# 停止服务
supervisorctl stop workreport

# 恢复备份
cp $BACKUP_DIR/work_report_backup /opt/work_report -r
chown -R www-data:www-data /opt/work_report

# 重启服务
supervisorctl start workreport
```

## ⚠️ 关键注意事项

1. **永远先备份**：任何部署操作前都必须备份数据库
2. **测试迁移**：在生产环境运行迁移前，先在测试环境验证
3. **增量更新**：优先使用Git拉取，避免完整替换
4. **权限检查**：确保数据库文件权限正确（www-data:www-data 664）
5. **数据验证**：部署后必须验证用户数据完整性
6. **监控日志**：密切关注应用和服务器日志
7. **回滚准备**：确保能快速回滚到上一个稳定版本

## 🔍 故障排查

### 数据丢失检查
```bash
# 1. 检查备份目录
ls -la /opt/backups/

# 2. 搜索可能的数据库文件
find /opt /var -name "*.sqlite3" -type f 2>/dev/null

# 3. 检查Git历史
cd /opt/work_report
git log --oneline -10

# 4. 恢复到指定版本
git reset --hard <commit-hash>
```

### 服务恢复
```bash
# 1. 检查服务状态
supervisorctl status
systemctl status nginx

# 2. 重启所有服务
supervisorctl restart all
systemctl restart nginx

# 3. 检查日志
tail -f /opt/work_report/logs/gunicorn.log
tail -f /var/log/nginx/error.log
```
