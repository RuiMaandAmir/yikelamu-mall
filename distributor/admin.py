from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.html import format_html
from django.db import models
from .models import (
    DistributionRule,
    Commission,
    Withdrawal,
    WithdrawalAudit,
    DistributorStats,
    DistributorReport,
    UpgradeRule,
    UpgradeRecord
)

@admin.register(DistributionRule)
class DistributionRuleAdmin(admin.ModelAdmin):
    list_display = ['level', 'commission_rate_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'level']
    search_fields = ['level']
    ordering = ['level']

    def commission_rate_display(self, obj):
        return format_html('{}%', obj.commission_rate * 100)
    commission_rate_display.short_description = _('佣金比例')

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = [
        'distributor',
        'order_link',
        'level',
        'amount',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'level', 'created_at']
    search_fields = ['distributor__username', 'order__order_number']
    readonly_fields = ['distributor', 'order', 'level', 'amount', 'created_at']
    
    fieldsets = [
        (_('佣金信息'), {
            'fields': [
                'distributor',
                'order',
                'level',
                'amount',
                'status'
            ]
        }),
        (_('时间信息'), {
            'fields': [
                'created_at',
                'settled_at'
            ]
        }),
    ]

    def order_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/trade/order/{obj.order.id}/change/',
            obj.order.order_number
        )
    order_link.short_description = _('订单')

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            if obj.status == 'settled':
                obj.settled_at = timezone.now()
        super().save_model(request, obj, form, change)

class WithdrawalAuditInline(admin.TabularInline):
    model = WithdrawalAudit
    extra = 0
    readonly_fields = ['auditor', 'action', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = [
        'distributor',
        'amount',
        'status',
        'bank_name',
        'account_holder',
        'created_at',
        'handled_at'
    ]
    list_filter = ['status', 'created_at', 'bank_name']
    search_fields = [
        'distributor__username',
        'bank_account',
        'account_holder'
    ]
    readonly_fields = [
        'distributor',
        'amount',
        'created_at',
        'handled_at',
        'handled_by'
    ]
    inlines = [WithdrawalAuditInline]
    
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
    
    actions = ['approve_withdrawals', 'reject_withdrawals', 'complete_withdrawals']
    
    def approve_withdrawals(self, request, queryset):
        for withdrawal in queryset.filter(status='pending'):
            withdrawal.status = 'approved'
            withdrawal.handled_by = request.user
            withdrawal.handled_at = timezone.now()
            withdrawal.save()
            
            WithdrawalAudit.objects.create(
                withdrawal=withdrawal,
                auditor=request.user,
                action='approve',
                remark='批量审核通过'
            )
    approve_withdrawals.short_description = _('批量审核通过')

    def reject_withdrawals(self, request, queryset):
        for withdrawal in queryset.filter(status='pending'):
            withdrawal.status = 'rejected'
            withdrawal.handled_by = request.user
            withdrawal.handled_at = timezone.now()
            withdrawal.save()
            
            # 返还提现金额
            withdrawal.distributor.balance += withdrawal.amount
            withdrawal.distributor.save()
            
            WithdrawalAudit.objects.create(
                withdrawal=withdrawal,
                auditor=request.user,
                action='reject',
                remark='批量审核拒绝'
            )
    reject_withdrawals.short_description = _('批量审核拒绝')

    def complete_withdrawals(self, request, queryset):
        for withdrawal in queryset.filter(status='approved'):
            withdrawal.status = 'completed'
            withdrawal.handled_by = request.user
            withdrawal.handled_at = timezone.now()
            withdrawal.save()
            
            WithdrawalAudit.objects.create(
                withdrawal=withdrawal,
                auditor=request.user,
                action='complete',
                remark='批量完成打款'
            )
    complete_withdrawals.short_description = _('批量完成打款')

@admin.register(DistributorStats)
class DistributorStatsAdmin(admin.ModelAdmin):
    list_display = [
        'distributor',
        'total_sales_display',
        'total_commission_display',
        'team_size',
        'order_count',
        'last_order_time'
    ]
    list_filter = ['last_order_time']
    search_fields = ['distributor__username']
    readonly_fields = [
        'distributor',
        'total_sales',
        'total_commission',
        'team_size',
        'order_count',
        'last_order_time'
    ]

    def total_sales_display(self, obj):
        return format_html('￥{:,.2f}', obj.total_sales)
    total_sales_display.short_description = _('总销售额')

    def total_commission_display(self, obj):
        return format_html('￥{:,.2f}', obj.total_commission)
    total_commission_display.short_description = _('总佣金')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(DistributorReport)
class DistributorReportAdmin(admin.ModelAdmin):
    list_display = [
        'period',
        'date',
        'total_sales_display',
        'total_commission_display',
        'order_count',
        'distributor_count',
        'new_distributor_count',
        'active_distributor_count',
        'withdrawal_amount_display'
    ]
    list_filter = ['period', 'date']
    date_hierarchy = 'date'
    readonly_fields = [field.name for field in DistributorReport._meta.fields]

    def total_sales_display(self, obj):
        return format_html('￥{:,.2f}', obj.total_sales)
    total_sales_display.short_description = _('总销售额')

    def total_commission_display(self, obj):
        return format_html('￥{:,.2f}', obj.total_commission)
    total_commission_display.short_description = _('总佣金')

    def withdrawal_amount_display(self, obj):
        return format_html('￥{:,.2f}', obj.withdrawal_amount)
    withdrawal_amount_display.short_description = _('提现金额')

@admin.register(UpgradeRule)
class UpgradeRuleAdmin(admin.ModelAdmin):
    list_display = [
        'target_level',
        'min_sales_display',
        'min_team_size',
        'min_direct_members',
        'min_duration_days',
        'is_active',
        'created_at'
    ]
    list_filter = ['is_active', 'target_level']
    search_fields = ['target_level']

    def min_sales_display(self, obj):
        return format_html('￥{:,.2f}', obj.min_sales)
    min_sales_display.short_description = _('最低销售额')

@admin.register(UpgradeRecord)
class UpgradeRecordAdmin(admin.ModelAdmin):
    list_display = [
        'distributor',
        'from_level',
        'to_level',
        'total_sales_display',
        'team_size',
        'direct_members',
        'duration_days',
        'created_at'
    ]
    list_filter = ['from_level', 'to_level', 'created_at']
    search_fields = ['distributor__username']
    readonly_fields = [field.name for field in UpgradeRecord._meta.fields]

    def total_sales_display(self, obj):
        return format_html('￥{:,.2f}', obj.total_sales)
    total_sales_display.short_description = _('当前销售额')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# 自定义管理站点标题
admin.site.site_header = _('伊客拉穆商城管理系统')
admin.site.site_title = _('伊客拉穆商城')
admin.site.index_title = _('管理中心')