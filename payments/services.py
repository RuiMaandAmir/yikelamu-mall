from django.utils import timezone
from django.db import transaction
import logging
from .utils import WeChatPay
from trade.models import Order

logger = logging.getLogger('payment')

class PaymentService:
    @staticmethod
    def create_payment(order, user_ip, openid):
        """创建支付订单"""
        try:
            result = WeChatPay.create_unified_order(order, user_ip, openid)
            logger.info(f"Payment created for order {order.order_number}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error creating payment for order {order.order_number}: {str(e)}")
            return {
                'success': False,
                'error_msg': '创建支付订单失败'
            }

    @staticmethod
    def process_refund(order, refund_amount, refund_reason):
        """处理退款"""
        try:
            with transaction.atomic():
                if order.status not in ['paid', 'shipped', 'delivered']:
                    logger.warning(f"Invalid order status for refund: {order.order_number}")
                    return {
                        'success': False,
                        'error_msg': '订单状态不允许退款'
                    }
                
                if refund_amount > order.actual_amount:
                    logger.warning(f"Refund amount exceeds order amount: {order.order_number}")
                    return {
                        'success': False,
                        'error_msg': '退款金额不能大于订单金额'
                    }
                
                result = WeChatPay.apply_refund(order, refund_amount, refund_reason)
                
                if result['success']:
                    order.status = 'refunded'
                    order.save()
                    logger.info(f"Refund successful for order {order.order_number}")
                else:
                    logger.error(f"Refund failed for order {order.order_number}: {result['error_msg']}")
                
                return result
                
        except Exception as e:
            logger.error(f"Error processing refund for order {order.order_number}: {str(e)}")
            return {
                'success': False,
                'error_msg': '退款处理失败'
            }

    @staticmethod
    def query_payment_status(order):
        """查询支付状态"""
        try:
            result = WeChatPay.query_order(order.order_number)
            logger.info(f"Payment status query for order {order.order_number}: {result}")
            
            if result['success'] and result['paid'] and order.status == 'pending':
                with transaction.atomic():
                    order.status = 'paid'
                    order.paid_at = timezone.now()
                    order.save()
                    logger.info(f"Order {order.order_number} status updated to paid")
            
            return result
            
        except Exception as e:
            logger.error(f"Error querying payment status for order {order.order_number}: {str(e)}")
            return {
                'success': False,
                'error_msg': '查询支付状态失败'
            }