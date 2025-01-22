import uuid
import time
from django.utils import timezone

def generate_order_number():
    """生成订单号"""
    # 格式：年月日时分秒+随机数
    return f"{timezone.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4().hex)[:6].upper()}"

def format_price(price):
    """将金额转换为分"""
    return int(float(price) * 100)

def deformat_price(price):
    """将分转换为元"""
    return float(price) / 100