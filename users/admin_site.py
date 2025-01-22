from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class CustomAdminSite(AdminSite):
    # 文本翻译
    site_title = _('伊客拉穆商城')
    site_header = _('伊客拉穆商城管理系统')
    index_title = _('管理中心')

    def get_app_list(self, request):
        """
        自定义应用列表的显示名称
        """
        app_list = super().get_app_list(request)
        for app in app_list:
            if app['app_label'] == 'auth':
                app['name'] = _('权限管理')
                for model in app['models']:
                    if model['object_name'] == 'Group':
                        model['name'] = _('用户组')
                    elif model['object_name'] == 'Permission':
                        model['name'] = _('权限')
            # 添加其他应用的翻译
        return app_list