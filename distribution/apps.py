from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DistributorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'distributor'
    verbose_name = _('分销管理')
