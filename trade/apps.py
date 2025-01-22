from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class TradeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trade'
    verbose_name = _('订单管理')