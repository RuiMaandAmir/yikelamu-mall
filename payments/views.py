from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging
from .services import PaymentService

logger = logging.getLogger('payment')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refund_order(request, order_id):
    """申请退款"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        refund_amount = Decimal(request.data.get('refund_amount'))
        refund_reason = request.data.get('refund_reason', '')
        
        result = PaymentService.process_refund(order, refund_amount, refund_reason)
        
        if result['success']:
            return Response(result)
        return Response({
            'error': result['error_msg']
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Order.DoesNotExist:
        return Response({
            'error': '订单不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Refund view error: {str(e)}")
        return Response({
            'error': '退款处理失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def query_payment_status(request, order_id):
    """查询支付状态"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        result = PaymentService.query_payment_status(order)
        
        if result['success']:
            return Response(result)
        return Response({
            'error': result['error_msg']
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Order.DoesNotExist:
        return Response({
            'error': '订单不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Query payment status view error: {str(e)}")
        return Response({
            'error': '查询支付状态失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)