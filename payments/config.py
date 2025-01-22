from django.conf import settings

# 微信支付配置
WECHAT_PAY_CONFIG = {
    'APP_ID': settings.WECHAT_CONFIG['APP_ID'],  # 小程序APP_ID
    'MCH_ID': 'your_mch_id',  # 商户号
    'API_KEY': 'your_api_key',  # API密钥
    'CERT_PATH': 'path/to/cert/apiclient_cert.pem',  # 证书路径
    'KEY_PATH': 'path/to/cert/apiclient_key.pem',  # 证书密钥路径
}

# 微信支付API地址
WECHAT_PAY_URLS = {
    'UNIFIED_ORDER': 'https://api.mch.weixin.qq.com/pay/unifiedorder',  # 统一下单
    'ORDER_QUERY': 'https://api.mch.weixin.qq.com/pay/orderquery',      # 订单查询
    'REFUND': 'https://api.mch.weixin.qq.com/secapi/pay/refund',        # 申请退款
    'REFUND_QUERY': 'https://api.mch.weixin.qq.com/pay/refundquery',    # 退款查询
}