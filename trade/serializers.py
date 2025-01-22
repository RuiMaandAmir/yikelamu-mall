from rest_framework import serializers
from .models import Cart, Order, OrderItem
from goods.serializers import GoodsListSerializer

class CartSerializer(serializers.ModelSerializer):
    """购物车序列化器"""
    goods_info = GoodsListSerializer(source='goods', read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    commission_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            'id', 'goods', 'goods_info', 'quantity',
            'selected', 'total_amount', 'commission_amount',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("商品数量不能小于1")
        return value

    def validate(self, attrs):
        goods = attrs.get('goods')
        quantity = attrs.get('quantity', 1)
        
        if not goods.is_on_sale:
            raise serializers.ValidationError("该商品已下架")
        
        if goods.stock < quantity:
            raise serializers.ValidationError(f"商品库存不足，当前库存{goods.stock}")
            
        return attrs

class CartSettlementSerializer(serializers.Serializer):
    """购物车结算序列化器"""
    cart_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    address_id = serializers.IntegerField(required=True)
    remark = serializers.CharField(required=False, allow_blank=True)