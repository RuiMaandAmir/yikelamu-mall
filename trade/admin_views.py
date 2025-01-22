from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils import timezone
from .services import OrderStatisticsService

@staff_member_required
def order_statistics_view(request):
    """订单统计视图"""
    context = {
        'summary': OrderStatisticsService.get_order_summary(),
        'daily_stats': OrderStatisticsService.get_daily_statistics(),
        'title': '订单统计',
    }
    return render(request, 'admin/order_statistics.html', context)