from django.conf import settings

# 微信支付配置
WECHAT_PAY = {
    'APP_ID': 'your_app_id',
    'MCH_ID': 'your_mch_id',
    'API_KEY': 'your_api_key',
    'NOTIFY_URL': f"{settings.BASE_URL}/api/trade/payment/wechat/notify/",
}

# 支付宝配置
ALIPAY = {
    'APP_ID': 'your_app_id',
    'PRIVATE_KEY_PATH': 'path/to/private_key.pem',
    'PUBLIC_KEY_PATH': 'path/to/public_key.pem',
    'NOTIFY_URL': f"{settings.BASE_URL}/api/trade/payment/alipay/notify/",
}