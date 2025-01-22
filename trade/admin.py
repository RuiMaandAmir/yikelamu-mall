from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['goods_name', 'goods_image', 'price', 'quantity', 'total_amount']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 
        'user', 
        'total_amount', 
        'actual_amount',
        'status',
        'receiver_name',
        'receiver_phone',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'receiver_name', 'receiver_phone']
    readonly_fields = [
        'order_number', 
        'user', 
        'total_amount', 
        'actual_amount',
        'commission_amount',
        'created_at',
        'paid_at',
        'shipped_at',
        'completed_at'
    ]
    
    fieldsets = [
        (_('订单信息'), {
            'fields': [
                'order_number', 
                'user', 
                'status',
                'total_amount', 
                'actual_amount'
            ]
        }),
        (_('收货信息'), {
            'fields': [
                'receiver_name',
                'receiver_phone',
                'receiver_address',
                'remark'
            ]
        }),
        (_('分销信息'), {
            'fields': [
                'distributor',
                'commission_amount'
            ]
        }),
        (_('时间信息'), {
            'fields': [
                'created_at',
                'paid_at',
                'shipped_at',
                'completed_at'
            ]
        }),
    ]
    
    inlines = [OrderItemInline]
    
    def has_add_permission(self, request):
        return False  # 禁止在管理界面手动创建订单

# Register your models here.
