from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from goods.models import Goods

class Order(models.Model):
    """订单模型"""
    ORDER_STATUS = (
        ('pending', _('待支付')),
        ('paid', _('已支付')),
        ('shipped', _('已发货')),
        ('delivered', _('已送达')),
        ('completed', _('已完成')),
        ('cancelled', _('已取消')),
        ('refunding', _('退款中')),
        ('refunded', _('已退款')),
    )

    order_number = models.CharField(_('订单编号'), max_length=32, unique=True)
    user = models.ForeignKey(User, verbose_name=_('用户'), on_delete=models.CASCADE)
    total_amount = models.DecimalField(_('订单总额'), max_digits=10, decimal_places=2)
    actual_amount = models.DecimalField(_('实付金额'), max_digits=10, decimal_places=2)
    status = models.CharField(_('订单状态'), max_length=20, choices=ORDER_STATUS, default='pending')
    
    # 收货信息
    receiver_name = models.CharField(_('收货人'), max_length=50)
    receiver_phone = models.CharField(_('收货电话'), max_length=20)
    receiver_address = models.TextField(_('收货地址'))
    
    # 订单备注
    remark = models.TextField(_('订单备注'), blank=True)
    
    # 分销相关
    distributor = models.ForeignKey(
        User, 
        verbose_name=_('分销商'), 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='distributed_orders'
    )
    commission_amount = models.DecimalField(
        _('佣金金额'), 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    paid_at = models.DateTimeField(_('支付时间'), null=True, blank=True)
    shipped_at = models.DateTimeField(_('发货时间'), null=True, blank=True)
    completed_at = models.DateTimeField(_('完成时间'), null=True, blank=True)

    class Meta:
        verbose_name = _('订单')
        verbose_name_plural = _('订单管理')
        ordering = ['-created_at']

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    """订单项模型"""
    order = models.ForeignKey(
        Order, 
        verbose_name=_('订单'), 
        on_delete=models.CASCADE,
        related_name='items'
    )
    goods = models.ForeignKey(
        Goods, 
        verbose_name=_('商品'), 
        on_delete=models.SET_NULL,
        null=True
    )
    goods_name = models.CharField(_('商品名称'), max_length=100)
    goods_image = models.CharField(_('商品图片'), max_length=200)
    price = models.DecimalField(_('商品单价'), max_digits=10, decimal_places=2)
    quantity = models.IntegerField(_('购买数量'))
    total_amount = models.DecimalField(_('总金额'), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('订单项')
        verbose_name_plural = _('订单项')

    def __str__(self):
        return f"{self.order.order_number} - {self.goods_name}"

# 在现有代码后添加购物车模型
class Cart(models.Model):
    """购物车模型"""
    user = models.ForeignKey(
        User,
        verbose_name=_('用户'),
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    goods = models.ForeignKey(
        Goods,
        verbose_name=_('商品'),
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        _('数量'),
        default=1
    )
    selected = models.BooleanField(
        _('是否选中'),
        default=True
    )
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('更新时间'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('购物车')
        verbose_name_plural = _('购物车管理')
        ordering = ['-created_at']
        unique_together = ['user', 'goods']

    def __str__(self):
        return f"{self.user.username} - {self.goods.name}"

    @property
    def total_amount(self):
        """计算小计金额"""
        return self.goods.price * self.quantity

    @property
    def commission_amount(self):
        """计算预计佣金"""
        if not self.user.role or self.user.role == 1:  # 普通用户没有佣金
            return Decimal('0.00')
        
        total = self.total_amount
        if self.user.role == 2:  # 普通分销商
            return (total * self.goods.commission_rate_1 / 100).quantize(Decimal('0.01'))
        elif self.user.role == 3:  # 高级分销商
            return (total * (self.goods.commission_rate_1 + self.goods.commission_rate_2) / 100).quantize(Decimal('0.01'))
        return Decimal('0.00')
