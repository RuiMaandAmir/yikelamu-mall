import os
from celery import Celery

# 设置 Django 默认配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 创建 Celery 实例
app = Celery('yikelamu')

# 使用 Django 的配置文件配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现异步任务
app.autodiscover_tasks()