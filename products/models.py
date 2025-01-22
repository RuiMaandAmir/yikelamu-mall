from django.db import models

class Category(models.Model):
    """商品分类"""
    name = models.CharField('分类名称', max_length=50)
    parent = models.ForeignKey('self', verbose_name='父类别', null=True, blank=True, on_delete=models.CASCADE)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'
        ordering = ['order']

    def __str__(self):
        return self.name

class Product(models.Model):
    """商品"""
    name = models.CharField('商品名称', max_length=100)
    category = models.ForeignKey(Category, verbose_name='商品分类', on_delete=models.CASCADE)
    price = models.DecimalField('售价', max_digits=10, decimal_places=2)
    original_price = models.DecimalField('原价', max_digits=10, decimal_places=2)
    stock = models.IntegerField('库存', default=0)
    sales = models.IntegerField('销量', default=0)
    image = models.ImageField('主图', upload_to='products/')
    description = models.TextField('商品描述')
    is_active = models.BooleanField('是否上架', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品管理'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

# Create your models here.
