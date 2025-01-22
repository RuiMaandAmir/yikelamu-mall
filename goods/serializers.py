from rest_framework import serializers
from .models import Category, Goods, GoodsImage, GoodsSpecification

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'sort_order']

class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ['id', 'image', 'sort_order']

class GoodsSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsSpecification
        fields = ['id', 'name', 'value', 'sort_order']

class GoodsListSerializer(serializers.ModelSerializer):
    """商品列表序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    commission = serializers.SerializerMethodField()

    class Meta:
        model = Goods
        fields = [
            'id', 'name', 'cover', 'price', 'original_price',
            'sales', 'category_name', 'is_on_sale', 'commission'
        ]

    def get_commission(self, obj):
        """根据用户角色返回佣金信息"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
            
        user = request.user
        if user.role == 2:  # 普通分销商
            return {
                'rate': obj.commission_rate_1,
                'amount': (obj.price * obj.commission_rate_1 / 100).quantize(Decimal('0.01'))
            }
        elif user.role == 3:  # 高级分销商
            return {
                'rate': obj.commission_rate_1,
                'amount': (obj.price * obj.commission_rate_1 / 100).quantize(Decimal('0.01')),
                'second_rate': obj.commission_rate_2,
                'second_amount': (obj.price * obj.commission_rate_2 / 100).quantize(Decimal('0.01'))
            }
        return None

class GoodsDetailSerializer(serializers.ModelSerializer):
    """商品详情序列化器"""
    category = CategorySerializer(read_only=True)
    images = GoodsImageSerializer(many=True, read_only=True)
    specifications = GoodsSpecificationSerializer(many=True, read_only=True)
    commission = serializers.SerializerMethodField()

    class Meta:
        model = Goods
        fields = [
            'id', 'category', 'name', 'cover', 'price',
            'original_price', 'stock', 'sales', 'description',
            'is_on_sale', 'images', 'specifications', 'commission',
            'created_at'
        ]

    def get_commission(self, obj):
        """与GoodsListSerializer中相同的佣金计算逻辑"""
        # 复用上面的佣金计算逻辑
        return GoodsListSerializer.get_commission(self, obj)