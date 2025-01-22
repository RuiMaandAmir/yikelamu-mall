from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging
from .models import Order
from payment.utils import WeChatPay

logger = logging.getLogger('order')

@shared_task
def check_order_timeout():
    """检查订单超时"""
    timeout_minutes = 30  # 设置超时时间为30分钟
    timeout_time = timezone.now() - timedelta(minutes=timeout_minutes)
    
    try:
        # 获取超时未支付的订单
        timeout_orders = Order.objects.filter(
            status='pending',
            created_at__lt=timeout_time
        )
        
        for order in timeout_orders:
            try:
                with transaction.atomic():
                    # 查询订单支付状态
                    payment_status = WeChatPay.query_order(order.order_number)
                    
                    if payment_status['success']:
                        if payment_status['paid']:
                            # 订单已支付但状态未更新
                            order.status = 'paid'
                            order.paid_at = timezone.now()
                            order.save()
                            logger.info(f"Order {order.order_number} status updated to paid")
                        else:
                            # 订单确实未支付，执行取消操作
                            order.status = 'cancelled'
                            order.save()
                            logger.info(f"Order {order.order_number} cancelled due to timeout")
                    else:
                        logger.error(f"Failed to query order {order.order_number} status: {payment_status['error_msg']}")
                        
            except Exception as e:
                logger.error(f"Error processing timeout order {order.order_number}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in check_order_timeout task: {str(e)}")