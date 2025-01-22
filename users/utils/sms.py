import random
import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('sms')

class SMSService:
    @staticmethod
    def generate_code():
        """生成6位验证码"""
        return str(random.randint(100000, 999999))
    
    @staticmethod
    def get_cache_key(phone):
        """获取缓存key"""
        return f"sms_code_{phone}"
    
    @classmethod
    def send_code(cls, phone):
        """发送验证码"""
        code = cls.generate_code()
        cache_key = cls.get_cache_key(phone)
        
        try:
            # 这里集成实际的短信发送服务
            # 测试环境下只打印验证码
            if settings.DEBUG:
                print(f"Send SMS to {phone}: {code}")
            else:
                # 实际短信发送逻辑
                pass
            
            # 将验证码存入缓存，5分钟有效
            cache.set(cache_key, code, timeout=300)
            logger.info(f"SMS code sent to {phone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone}: {str(e)}")
            return False
    
    @classmethod
    def verify_code(cls, phone, code):
        """验证验证码"""
        cache_key = cls.get_cache_key(phone)
        cached_code = cache.get(cache_key)
        
        if not cached_code:
            return False
        
        # 验证成功后删除缓存
        if str(code) == str(cached_code):
            cache.delete(cache_key)
            return True
            
        return False