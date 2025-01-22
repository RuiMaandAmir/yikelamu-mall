from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

class UserStatusFilter(SimpleListFilter):
    title = _('用户状态')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('active', _('活跃用户')),
            ('inactive', _('未激活用户')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)