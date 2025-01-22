from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """商品分类"""
    name = models.CharField(_('分类名称'), max_length=50)
    parent = models.ForeignKey('self', verbose_name=_('父类别'), null=True, blank=True, 
                             on_delete=models.CASCADE, related_name='children')
    order = models.IntegerField(_('排序'), default=0)
    is_active = models.BooleanField(_('是否启用'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('商品分类')
        verbose_name_plural = _('商品分类')
        ordering = ['order', 'id']

    def __str__(self):
        if self.parent:
            return f'{self.parent} - {self.name}'
        return self.name

class Goods(models.Model):
    """商品"""
    name = models.CharField(_('商品名称'), max_length=100)
    category = models.ForeignKey(Category, verbose_name=_('商品分类'), 
                               on_delete=models.CASCADE, related_name='goods')
    price = models.DecimalField(_('售价'), max_digits=10, decimal_places=2)
    original_price = models.DecimalField(_('原价'), max_digits=10, decimal_places=2)
    stock = models.IntegerField(_('库存'), default=0)
    sales = models.IntegerField(_('销量'), default=0)
    image = models.ImageField(_('主图'), upload_to='goods/%Y/%m')
    description = models.TextField(_('商品描述'))
    is_active = models.BooleanField(_('是否上架'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('商品')
        verbose_name_plural = _('商品管理')
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    

# Create your models here.
