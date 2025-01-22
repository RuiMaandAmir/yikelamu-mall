from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Category, Goods

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order', 'is_active', 'goods_count', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    ordering = ['order', 'id']
    list_editable = ['order', 'is_active']

    def goods_count(self, obj):
        return obj.goods.count()
    goods_count.short_description = _('商品数量')

@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'sales', 
                   'show_image', 'is_active', 'created_at']
    list_filter = ['is_active', 'category']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'is_active']
    readonly_fields = ['sales', 'created_at', 'updated_at', 'show_image']
    
    fieldsets = [
        (_('基本信息'), {
            'fields': ['name', 'category', 'image', 'show_image', 'description']
        }),
        (_('价格库存'), {
            'fields': ['price', 'original_price', 'stock', 'sales']
        }),
        (_('状态信息'), {
            'fields': ['is_active', 'created_at', 'updated_at']
        }),
    ]

    def show_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return _('暂无图片')
    show_image.short_description = _('商品图片')

# Register your models here.
