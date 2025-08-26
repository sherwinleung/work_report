"""
WorkReport 生产环境配置
"""
import os
from pathlib import Path
from .settings import *

# 生产环境安全配置
DEBUG = False
ALLOWED_HOSTS = [
    'your-domain.com',  # 替换为你的域名
    'www.your-domain.com',
    'your-server-ip',   # 替换为你的服务器IP
    '127.0.0.1',
    'localhost'
]

# 安全密钥（从环境变量获取）
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key-here')

# 数据库配置（生产环境建议使用MySQL或PostgreSQL）
if os.environ.get('DATABASE_URL'):
    # 支持DATABASE_URL格式（适用于云数据库）
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # MySQL配置示例
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'workreport'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 缓存配置（Redis）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24小时

# CSRF保护
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# 安全设置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS设置（如果使用HTTPS）
if os.environ.get('USE_HTTPS', 'false').lower() == 'true':
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'workreport': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# 邮件配置（用于错误通知）
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
    
    # 管理员邮箱（接收错误通知）
    ADMINS = [
        ('Admin', os.environ.get('ADMIN_EMAIL', '564999607@qq.com')),
    ]

# API密钥配置（从环境变量获取）
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'deepseek')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_API_BASE = os.environ.get('OPENAI_API_BASE', '')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_BASE = os.environ.get('DEEPSEEK_API_BASE', 'https://api.deepseek.com')

# 默认API配置（用于新用户注册时自动创建）
DEFAULT_OPENAI_API_KEY = os.environ.get('DEFAULT_OPENAI_API_KEY', 'sk-QLZDJaU1a8uuoYfdaN52FPzpoFFUmPlhEOmgmyMZ5g=')
DEFAULT_OPENAI_API_BASE = os.environ.get('DEFAULT_OPENAI_API_BASE', 'https://llmhub.app')
DEFAULT_DEEPSEEK_API_KEY = os.environ.get('DEFAULT_DEEPSEEK_API_KEY', 'sk-d40ba7f7a4b242268876d3ca27d72684')
DEFAULT_DEEPSEEK_API_BASE = os.environ.get('DEFAULT_DEEPSEEK_API_BASE', 'https://api.deepseek.com')
