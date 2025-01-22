from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Cart, Order, OrderItem
from .serializers import CartSerializer, CartSettlementSerializer

class CartViewSet(viewsets.ModelViewSet):
    """购物车视图集"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """创建购物车记录"""
        goods = serializer.validated_data['goods']
        quantity = serializer.validated_data.get('quantity', 1)
        
        cart_item = Cart.objects.filter(
            user=self.request.user,
            goods=goods
        ).first()
        
        if cart_item:
            cart_item.quantity += quantity
            cart_item.save()
            serializer.instance = cart_item
        else:
            serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """购物车汇总信息"""
        queryset = self.get_queryset().filter(selected=True)
        total_quantity = queryset.aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        total_amount = Decimal('0.00')
        total_commission = Decimal('0.00')
        
        for item in queryset:
            total_amount += item.total_amount
            total_commission += item.commission_amount
        
        return Response({
            'total_quantity': total_quantity,
            'total_amount': total_amount,
            'total_commission': total_commission
        })

    @action(detail=False, methods=['post'])
    def settle(self, request):
        """购物车结算"""
        serializer = CartSettlementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart_items = Cart.objects.filter(
            user=request.user,
            id__in=serializer.validated_data['cart_ids']
        )
        
        if not cart_items.exists():
            return Response(
                {"error": "未选择商品"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 检查商品库存和状态
        for item in cart_items:
            if not item.goods.is_on_sale:
                return Response(
                    {"error": f"商品 {item.goods.name} 已下架"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if item.goods.stock < item.quantity:
                return Response(
                    {"error": f"商品 {item.goods.name} 库存不足"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            with transaction.atomic():
                # 创建订单
                order = Order.objects.create(
                    user=request.user,
                    order_number=generate_order_number(),  # 需要实现此函数
                    total_amount=sum(item.total_amount for item in cart_items),
                    actual_amount=sum(item.total_amount for item in cart_items),  # 这里可以加入优惠逻辑
                    commission_amount=sum(item.commission_amount for item in cart_items),
                    distributor=request.user if request.user.role in [2, 3] else None,
                    remark=serializer.validated_data.get('remark', '')
                    # 需要添加收货地址信息
                )
                
                # 创建订单项
                order_items = []
                for cart_item in cart_items:
                    order_items.append(OrderItem(
                        order=order,
                        goods=cart_item.goods,
                        goods_name=cart_item.goods.name,
                        goods_image=cart_item.goods.cover.url,
                        price=cart_item.goods.price,
                        quantity=cart_item.quantity,
                        total_amount=cart_item.total_amount
                    ))
                
                OrderItem.objects.bulk_create(order_items)
                
                # 删除已结算的购物车项
                cart_items.delete()
                
                return Response({
                    "order_id": order.id,
                    "order_number": order.order_number
                })
                
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """清空购物车"""
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)