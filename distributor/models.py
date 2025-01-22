from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class CommissionRecord(models.Model):
    """佣金记录"""
    STATUS_CHOICES = (
        ('pending', _('待结算')),
        ('settled', _('已结算')),
        ('refunded', _('已退款')),
        ('failed', _('结算失败')),
    )

    distributor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('分销商'),
        related_name='commission_records'
    )
    order = models.ForeignKey(
        'trade.Order',
        on_delete=models.CASCADE,
        verbose_name=_('关联订单'),
        related_name='commission_records'
    )
    amount = models.DecimalField(
        _('佣金金额'),
        max_digits=10,
        decimal_places=2
    )
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    remark = models.TextField(
        _('备注'),
        blank=True
    )
    created_at = models.DateTimeField(
        _('创建时间'),
        auto_now_add=True
    )
    settled_at = models.DateTimeField(
        _('结算时间'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('佣金记录')
        verbose_name_plural = _('佣金记录')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.distributor.username} - {self.amount}"

class CommissionWithdrawal(models.Model):
    """佣金提现"""
    STATUS_CHOICES = (
        ('pending', _('待审核')),
        ('approved', _('已通过')),
        ('rejected', _('已拒绝')),
        ('completed', _('已完成')),
    )

    distributor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('分销商'),
        related_name='withdrawals'
    )
    amount = models.DecimalField(
        _('提现金额'),
        max_digits=10,
        decimal_places=2
    )
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    remark = models.TextField(
        _('备注'),
        blank=True
    )
    created_at = models.DateTimeField(
        _('申请时间'),
        auto_now_add=True
    )
    completed_at = models.DateTimeField(
        _('完成时间'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('佣金提现')
        verbose_name_plural = _('佣金提现')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.distributor.username} - {self.amount}"