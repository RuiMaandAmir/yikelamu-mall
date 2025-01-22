from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import DistributionRule, Commission, Withdrawal

@admin.register(DistributionRule)
class DistributionRuleAdmin(admin.ModelAdmin):
    list_display = ['level', 'commission_rate_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'level']
    search_fields = ['level']

    def commission_rate_display(self, obj):
        return f"{obj.commission_rate * 100}%"
    commission_rate_display.short_description = _('佣金比例')

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = [
        'distributor',
        'order',
        'level',
        'amount',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'level', 'created_at']
    search_fields = ['distributor__username', 'order__order_number']
    readonly_fields = ['distributor', 'order', 'level', 'amount', 'created_at']

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = [
        'distributor',
        'amount',
        'status',
        'bank_name',
        'account_holder',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'distributor__username',
        'bank_name',
        'bank_account',
        'account_holder'
    ]
    readonly_fields = ['distributor', 'amount', 'created_at']
    
    fieldsets = [
        (_('基本信息'), {
            'fields': [
                'distributor',
                'amount',
                'status'
            ]
        }),
        (_('银行信息'), {
            'fields': [
                'bank_name',
                'bank_account',
                'account_holder'
            ]
        }),
        (_('处理信息'), {
            'fields': [
                'handled_by',
                'handled_at',
                'remark'
            ]
        }),
    ]

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            obj.handled_by = request.user
            obj.handled_at = timezone.now()
        super().save_model(request, obj, form, change)

# Register your models here.
