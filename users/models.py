from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        (1, '普通用户'),
        (2, '分销商'),
        (3, '高级分销商'),
    )
    
    role = models.IntegerField(
        choices=ROLE_CHOICES, 
        default=1, 
        verbose_name='用户角色'
    )
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        verbose_name='上级分销商'
    )
    phone = models.CharField(
        max_length=11, 
        unique=True, 
        null=True, 
        verbose_name='手机号'
    )
    wechat_openid = models.CharField(
        max_length=100, 
        unique=True, 
        null=True, 
        verbose_name='微信OpenID'
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True, 
        verbose_name='头像'
    )
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='账户余额'
    )

    # 覆盖原有字段的显示名称
    username = models.CharField(
        _('用户名'),
        max_length=150,
        unique=True,
        help_text=_('必填。150个字符或者更少。包含字母，数字和仅有的@/./+/-/_符号。'),
        error_messages={
            'unique': _("该用户名已存在。"),
        },
    )
    first_name = models.CharField(_('名字'), max_length=150, blank=True)
    last_name = models.CharField(_('姓氏'), max_length=150, blank=True)
    email = models.EmailField(_('电子邮箱'), blank=True)
    is_staff = models.BooleanField(
        _('工作人员状态'),
        default=False,
        help_text=_('指定用户是否可以登录到这个管理站点。'),
    )
    is_active = models.BooleanField(
        _('激活状态'),
        default=True,
        help_text=_('指定是否应该将此用户视为活动用户。取消选择此项而不是删除帐户。'),
    )
    is_superuser = models.BooleanField(
        _('超级管理员状态'),
        default=False,
        help_text=_('指定该用户具有所有权限而无需明确分配它们。'),
    )
    date_joined = models.DateTimeField(_('注册时间'), auto_now_add=True)
    last_login = models.DateTimeField(_('最后登录'), null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('用户组'),
        blank=True,
        help_text=_('用户所属的组。一个用户将获得其所属组的所有权限。'),
        related_name="custom_user_set",
        related_query_name="user",
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('用户权限'),
        blank=True,
        help_text=_('为该用户特别指定的权限。'),
        related_name="custom_user_set",
        related_query_name="user",
    )

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username