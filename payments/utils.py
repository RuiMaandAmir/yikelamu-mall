import hashlib
import time
import random
import string
import xml.etree.ElementTree as ET
import requests
from django.conf import settings
from .config import WECHAT_PAY_CONFIG, WECHAT_PAY_URLS
import logging
from datetime import datetime
from decimal import Decimal
logger = logging.getLogger('payment')


class WeChatPay:
    @staticmethod
    def generate_nonce_str(length=32):
        """生成随机字符串"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def dict_to_xml(data):
        """字典转XML"""
        xml_elements = ['<xml>']
        for k, v in data.items():
            xml_elements.append(f'<{k}>{v}</{k}>')
        xml_elements.append('</xml>')
        return ''.join(xml_elements)

    @staticmethod
    def xml_to_dict(xml_string):
        """XML转字典"""
        root = ET.fromstring(xml_string)
        return {child.tag: child.text for child in root}

    @classmethod
    def generate_sign(cls, data, api_key):
        """生成签名"""
        # 按字典序排序参数
        sorted_items = sorted(data.items())
        # 拼接字符串
        sign_string = '&'.join(f'{k}={v}' for k, v in sorted_items if v)
        # 加入API密钥
        sign_string = f'{sign_string}&key={api_key}'
        # MD5加密并转大写
        return hashlib.md5(sign_string.encode()).hexdigest().upper()

    @classmethod
    def create_unified_order(cls, order, user_ip, openid):
        """创建统一订单"""
        nonce_str = cls.generate_nonce_str()
        
        data = {
            'appid': WECHAT_PAY_CONFIG['APP_ID'],
            'mch_id': WECHAT_PAY_CONFIG['MCH_ID'],
            'nonce_str': nonce_str,
            'body': f'订单 {order.order_number}',
            'out_trade_no': order.order_number,
            'total_fee': int(order.actual_amount * 100),  # 转换为分
            'spbill_create_ip': user_ip,
            'notify_url': f'{settings.BASE_URL}/api/payment/callback/',
            'trade_type': 'JSAPI',
            'openid': openid
        }
        
        # 生成签名
        data['sign'] = cls.generate_sign(data, WECHAT_PAY_CONFIG['API_KEY'])
        
        # 转换为XML
        xml_data = cls.dict_to_xml(data)
        
        # 发送请求
        response = requests.post(WECHAT_PAY_URLS['UNIFIED_ORDER'], data=xml_data)
        result = cls.xml_to_dict(response.text)
        
        if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
            # 生成支付参数
            prepay_id = result.get('prepay_id')
            timestamp = str(int(time.time()))
            
            pay_params = {
                'appId': WECHAT_PAY_CONFIG['APP_ID'],
                'timeStamp': timestamp,
                'nonceStr': nonce_str,
                'package': f'prepay_id={prepay_id}',
                'signType': 'MD5'
            }
            
            # 生成支付签名
            pay_params['paySign'] = cls.generate_sign(pay_params, WECHAT_PAY_CONFIG['API_KEY'])
            
            return {
                'success': True,
                'pay_params': pay_params
            }
        
        return {
            'success': False,
            'error_msg': result.get('return_msg') or result.get('err_code_des')
        }

    @classmethod
    def verify_payment(cls, xml_data):
        """验证支付回调"""
        result = cls.xml_to_dict(xml_data)
        
        # 验证签名
        sign = result.pop('sign', None)
        if not sign or sign != cls.generate_sign(result, WECHAT_PAY_CONFIG['API_KEY']):
            return None
            
        if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
            return {
                'order_number': result.get('out_trade_no'),
                'transaction_id': result.get('transaction_id'),
                'paid_amount': float(result.get('total_fee', 0)) / 100,  # 转换为元
                'paid_at': result.get('time_end')
            }
            
        return None

    @classmethod
    def query_order(cls, order_number):
        """查询订单状态"""
        data = {
            'appid': WECHAT_PAY_CONFIG['APP_ID'],
            'mch_id': WECHAT_PAY_CONFIG['MCH_ID'],
            'out_trade_no': order_number,
            'nonce_str': cls.generate_nonce_str()
        }
        
        data['sign'] = cls.generate_sign(data, WECHAT_PAY_CONFIG['API_KEY'])
        xml_data = cls.dict_to_xml(data)
        
        response = requests.post(WECHAT_PAY_URLS['ORDER_QUERY'], data=xml_data)
        result = cls.xml_to_dict(response.text)
        
        if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
            trade_state = result.get('trade_state')
            return {
                'success': True,
                'paid': trade_state == 'SUCCESS',
                'trade_state': trade_state,
                'trade_state_desc': result.get('trade_state_desc')
            }
            
        return {
            'success': False,
            'error_msg': result.get('return_msg') or result.get('err_code_des')
        }
    @classmethod
    def apply_refund(cls, order, refund_amount, refund_reason):
        """申请退款"""
        try:
            data = {
                'appid': WECHAT_PAY_CONFIG['APP_ID'],
                'mch_id': WECHAT_PAY_CONFIG['MCH_ID'],
                'nonce_str': cls.generate_nonce_str(),
                'out_trade_no': order.order_number,
                'out_refund_no': f'refund_{order.order_number}',
                'total_fee': int(order.actual_amount * 100),
                'refund_fee': int(refund_amount * 100),
                'refund_desc': refund_reason[:80],  # 微信限制80字符
            }
            
            data['sign'] = cls.generate_sign(data, WECHAT_PAY_CONFIG['API_KEY'])
            xml_data = cls.dict_to_xml(data)
            
            # 使用证书发送请求
            response = requests.post(
                WECHAT_PAY_URLS['REFUND'],
                data=xml_data,
                cert=(WECHAT_PAY_CONFIG['CERT_PATH'], WECHAT_PAY_CONFIG['KEY_PATH'])
            )
            
            result = cls.xml_to_dict(response.text)
            logger.info(f"Refund request result for order {order.order_number}: {result}")
            
            if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
                return {
                    'success': True,
                    'refund_id': result.get('refund_id'),
                    'refund_fee': float(result.get('refund_fee', 0)) / 100
                }
            
            error_msg = result.get('err_code_des') or result.get('return_msg')
            logger.error(f"Refund failed for order {order.order_number}: {error_msg}")
            return {
                'success': False,
                'error_msg': error_msg
            }
            
        except Exception as e:
            logger.error(f"Refund error for order {order.order_number}: {str(e)}")
            return {
                'success': False,
                'error_msg': str(e)
            }

    @classmethod
    def query_refund_status(cls, order_number):
        """查询退款状态"""
        try:
            data = {
                'appid': WECHAT_PAY_CONFIG['APP_ID'],
                'mch_id': WECHAT_PAY_CONFIG['MCH_ID'],
                'out_trade_no': order_number,
                'nonce_str': cls.generate_nonce_str()
            }
            
            data['sign'] = cls.generate_sign(data, WECHAT_PAY_CONFIG['API_KEY'])
            xml_data = cls.dict_to_xml(data)
            
            response = requests.post(WECHAT_PAY_URLS['REFUND_QUERY'], data=xml_data)
            result = cls.xml_to_dict(response.text)
            
            logger.info(f"Refund query result for order {order_number}: {result}")
            
            if result.get('return_code') == 'SUCCESS' and result.get('result_code') == 'SUCCESS':
                return {
                    'success': True,
                    'refund_status': result.get('refund_status_0'),
                    'refund_fee': float(result.get('refund_fee_0', 0)) / 100
                }
            
            error_msg = result.get('err_code_des') or result.get('return_msg')
            logger.error(f"Refund query failed for order {order_number}: {error_msg}")
            return {
                'success': False,
                'error_msg': error_msg
            }
            
        except Exception as e:
            logger.error(f"Refund query error for order {order_number}: {str(e)}")
            return {
                'success': False,
                'error_msg': str(e)
            }