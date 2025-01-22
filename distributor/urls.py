from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'distributors', views.DistributorViewSet, basename='distributor')
router.register(r'commissions', views.CommissionViewSet, basename='commission')
router.register(r'withdrawals', views.WithdrawalViewSet, basename='withdrawal')

urlpatterns = [
    path('', include(router.urls)),
]