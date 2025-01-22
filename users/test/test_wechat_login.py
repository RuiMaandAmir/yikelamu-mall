from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from users.utils.wechat import WeChatAPI

User = get_user_model()

class WeChatLoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    @patch.object(WeChatAPI, 'code2session')
    def test_wechat_login(self, mock_code2session):
        # 模拟微信返回数据
        mock_code2session.return_value = {
            'openid': 'test_openid',
            'session_key': 'test_session_key'
        }
        
        # 测试登录
        response = self.client.post('/api/users/wechat_login/', {
            'code': 'test_code',
            'nickname': 'Test User',
            'avatar': 'http://example.com/avatar.jpg'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('refresh', response.data)
        
        # 验证用户是否被创建
        user = User.objects.get(wechat_openid='test_openid')
        self.assertIsNotNone(user)
        self.assertEqual(user.avatar, 'http://example.com/avatar.jpg')