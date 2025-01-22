from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from trade.models import Order

class DistributionRule(models.Model):
    """分销规则"""
    LEVEL_CHOICES = (
        (1, '一级分销'),
        (2, '二级分销'),
        (3, '三级分销'),
    )

    level = models.IntegerField(_('分销等级'), choices=LEVEL_CHOICES)
    commission_rate = models.DecimalField(
        _('佣金比例'), 
        max_digits=4, 
        decimal_places=2,
        help_text=_('例如：0.10 表示 10%')
    )
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('分销规则')
        verbose_name_plural = _('分销规则')
        unique_together = ['level']
        ordering = ['level']

    def __str__(self):
        return f"{self.get_level_display()} - {self.commission_rate * 100}%"

class Commission(models.Model):
    """佣金记录"""
    STATUS_CHOICES = (
        ('pending', _('待结算')),
        ('settled', _('已结算')),
        ('cancelled', _('已取消')),
    )

    distributor = models.ForeignKey(
        User, 
        verbose_name=_('分销商'),
        on_delete=models.CASCADE,
        related_name='commissions'
    )
    order = models.ForeignKey(
        Order,
        verbose_name=_('关联订单'),
        on_delete=models.CASCADE,
        related_name='commissions'
    )
    level = models.IntegerField(_('分销等级'))
    amount = models.DecimalField(_('佣金金额'), max_digits=10, decimal_places=2)
    status = models.CharField(
        _('结算状态'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    settled_at = models.DateTimeField(_('结算时间'), null=True, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('佣金记录')
        verbose_name_plural = _('佣金记录')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.distributor.username} - {self.amount}"

class Withdrawal(models.Model):
    """提现申请"""
    STATUS_CHOICES = (
        ('pending', _('待审核')),
        ('approved', _('已通过')),
        ('rejected', _('已拒绝')),
        ('completed', _('已完成')),
    )

    distributor = models.ForeignKey(
        User,
        verbose_name=_('分销商'),
        on_delete=models.CASCADE,
        related_name='withdrawals'
    )
    amount = models.DecimalField(_('提现金额'), max_digits=10, decimal_places=2)
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    bank_name = models.CharField(_('银行名称'), max_length=100)
    bank_account = models.CharField(_('银行账号'), max_length=100)
    account_holder = models.CharField(_('开户人'), max_length=100)
    remark = models.TextField(_('备注'), blank=True)
    handled_by = models.ForeignKey(
        User,
        verbose_name=_('处理人'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_withdrawals'
    )
    handled_at = models.DateTimeField(_('处理时间'), null=True, blank=True)
    created_at = models.DateTimeField(_('申请时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('提现申请')
        verbose_name_plural = _('提现申请')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.distributor.username} - {self.amount}"

# Create your models here.
