from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:order_id>/', views.create_payment_view, name='create_payment'),
    path('callback/', views.payment_callback_view, name='payment_callback'),
]