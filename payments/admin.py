from django.contrib import admin
from django.utils.html import format_html
from .models import CommissionRecord
from trade.models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount', 'status', 
                   'payment_status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username']
    readonly_fields = ['order_number', 'created_at', 'paid_at']
    
    def payment_status(self, obj):
        if obj.status == 'pending':
            return format_html('<span style="color: orange;">待支付</span>')
        elif obj.status == 'paid':
            return format_html('<span style="color: green;">已支付</span>')
        elif obj.status == 'refunding':
            return format_html('<span style="color: red;">退款中</span>')
        elif obj.status == 'refunded':
            return format_html('<span style="color: gray;">已退款</span>')
        return obj.get_status_display()

@admin.register(CommissionRecord)
class CommissionRecordAdmin(admin.ModelAdmin):
    list_display = ['distributor', 'order', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['distributor__username', 'order__order_number']
    readonly_fields = ['created_at', 'settled_at']

    def has_add_permission(self, request):
        return False