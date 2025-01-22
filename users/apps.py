from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig

class CustomAdminConfig(AdminConfig):
    default_site = 'users.admin.CustomAdminSite'

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = '用户管理'

     # 暂时注释掉 signals 导入
    # def ready(self):