import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

class WeChatAPI:
    @staticmethod
    def code2session(code):
        """
        使用 code 换取 openid 和 session_key
        """
        url = settings.WECHAT_URLS['CODE2SESSION']
        params = {
            'appid': settings.WECHAT_CONFIG['APP_ID'],
            'secret': settings.WECHAT_CONFIG['APP_SECRET'],
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.get(url, params=params)
            result = response.json()
            
            if 'errcode' in result:
                raise AuthenticationFailed(f"微信登录失败: {result.get('errmsg')}")
                
            return {
                'openid': result.get('openid'),
                'session_key': result.get('session_key'),
                'unionid': result.get('unionid')  # 如果有unionid则返回
            }
        except Exception as e:
            raise AuthenticationFailed(f"微信登录异常: {str(e)}")