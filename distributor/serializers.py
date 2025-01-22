from rest_framework import serializers
from users.models import User
from .models import Commission, Withdrawal, DistributorStats

class DistributorSerializer(serializers.ModelSerializer):
    """分销商信息序列化器"""
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_commission = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    team_size = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'role', 
            'balance',
            'total_sales',
            'total_commission',
            'team_size'
        ]
        read_only_fields = ['balance']

class CommissionSerializer(serializers.ModelSerializer):
    """佣金记录序列化器"""
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Commission
        fields = [
            'id',
            'order_number',
            'level',
            'amount',
            'status',
            'created_at',
            'settled_at'
        ]
        read_only_fields = fields

class WithdrawalSerializer(serializers.ModelSerializer):
    """提现申请序列化器"""
    class Meta:
        model = Withdrawal
        fields = [
            'id',
            'amount',
            'status',
            'bank_name',
            'bank_account',
            'account_holder',
            'created_at',
            'handled_at'
        ]
        read_only_fields = ['status', 'created_at', 'handled_at']

    def validate_amount(self, value):
        user = self.context['request'].user
        if value > user.balance:
            raise serializers.ValidationError('提现金额不能大于可用余额')
        if value < 100:  # 最低提现金额限制
            raise serializers.ValidationError('提现金额不能小于100元')
        return value

class TeamMemberSerializer(serializers.ModelSerializer):
    """团队成员序列化器"""
    total_sales = serializers.DecimalField(
        source='stats.total_sales',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role',
            'total_sales',
            'date_joined'
        ]

class DistributorStatsSerializer(serializers.ModelSerializer):
    """分销商统计序列化器"""
    class Meta:
        model = DistributorStats
        fields = [
            'total_sales',
            'total_commission',
            'team_size',
            'order_count',
            'last_order_time'
        ]
        read_only_fields = fields