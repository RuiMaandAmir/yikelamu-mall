import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .utils.sms import SMSService
from .utils.token import TokenService

logger = logging.getLogger('users')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        elif self.action == 'me':
            return UserProfileSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'wechat_login']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def wechat_login(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': '需要微信授权码'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 这里需要实现微信登录逻辑
            # 1. 通过code获取openid
            # 2. 根据openid查找或创建用户
            # 3. 生成JWT token
            user = User.objects.get(wechat_openid=openid)
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def become_distributor(self, request):
        user = request.user
        parent_id = request.data.get('parent_id')

        if user.role != 1:
            return Response({'error': '您已经是分销商'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if parent_id:
                parent = User.objects.get(id=parent_id, role__in=[2, 3])
                user.parent = parent
            
            user.role = 2  # 设置为分销商
            user.save()
            
            return Response({'message': '成功成为分销商'})
        except User.DoesNotExist:
            return Response({'error': '上级分销商不存在'}, status=status.HTTP_400_BAD_REQUEST)
 @action(detail=False, methods=['post'])
    def wechat_login(self, request):
        """微信小程序登录"""
        serializer = WeChatLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 获取微信用户信息
        wx_data = WeChatAPI.code2session(serializer.validated_data['code'])
        
        # 获取或创建用户
        user, created = User.objects.get_or_create(
            wechat_openid=wx_data['openid'],
            defaults={
                'username': f"wx_{uuid.uuid4().hex[:8]}",  # 生成随机用户名
                'avatar': serializer.validated_data.get('avatar', ''),
                'is_active': True
            }
        )
        
        # 如果是新用户且提供了parent_id，设置上级分销商
        if created and serializer.validated_data.get('parent_id'):
            user.parent_id = serializer.validated_data['parent_id']
            user.save()
        
        # 更新用户信息
        if not created and serializer.validated_data.get('avatar'):
            user.avatar = serializer.validated_data['avatar']
            user.save()
        
        # 生成token
        refresh = RefreshToken.for_user(user)
        
        # 返回用户信息和token
        response_data = WeChatUserSerializer(user).data
        response_data.update({
            'token': str(refresh.access_token),
            'refresh': str(refresh)
        })
        
        return Response(response_data)

    @action(detail=False, methods=['post'])
    def bind_phone(self, request):
        """绑定手机号"""
        if not request.user.is_authenticated:
            return Response({'error': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)
            
        phone = request.data.get('phone')
        code = request.data.get('code')  # 验证码，实际项目中需要验证
        
        if not phone:
            return Response({'error': '请提供手机号'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 这里应该添加手机号验证码验证逻辑
        
        # 检查手机号是否已被使用
        if User.objects.filter(phone=phone).exclude(id=request.user.id).exists():
            return Response({'error': '该手机号已被使用'}, status=status.HTTP_400_BAD_REQUEST)
            
        request.user.phone = phone
        request.user.save()
        
        return Response({'message': '手机号绑定成功'})
 @action(detail=False, methods=['post'])
    def send_verification_code(self, request):
        """发送手机验证码"""
        phone = request.data.get('phone')
        
        if not phone:
            return Response({'error': '请提供手机号'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            if SMSService.send_code(phone):
                return Response({'message': '验证码已发送'})
            return Response({'error': '验证码发送失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Failed to send verification code: {str(e)}")
            return Response({'error': '系统错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def verify_phone(self, request):
        """验证手机号"""
        serializer = PhoneVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        
        try:
            if SMSService.verify_code(phone, code):
                request.user.phone = phone
                request.user.save()
                logger.info(f"Phone verified for user {request.user.id}")
                return Response({'message': '手机号验证成功'})
            return Response({'error': '验证码错误'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Phone verification failed: {str(e)}")
            return Response({'error': '验证失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def refresh_token(self, request):
        """刷新token"""
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': '请提供refresh token'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            tokens = TokenService.refresh_token(refresh_token)
            return Response(tokens)
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return Response({'error': '刷新token失败'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """更新用户信息"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f"Profile updated for user {request.user.id}")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Profile update failed: {str(e)}")
            return Response({'error': '更新失败'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bind_distributor(self, request):
        """绑定分销关系"""
        serializer = DistributorBindingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            parent_code = serializer.validated_data['parent_code']
            parent = User.objects.get(username=parent_code, role__in=[2, 3])
            
            # 检查是否已经是分销商
            if request.user.role != 1:
                return Response({'error': '您已经是分销商'}, status=status.HTTP_400_BAD_REQUEST)
                
            # 检查是否形成循环
            if parent.parent_id == request.user.id:
                return Response({'error': '不能形成循环的分销关系'}, status=status.HTTP_400_BAD_REQUEST)
                
            request.user.parent = parent
            request.user.role = 2  # 设置为分销商
            request.user.save()
            
            logger.info(f"Distributor relationship bound for user {request.user.id}")
            return Response({'message': '分销关系绑定成功'})
            
        except User.DoesNotExist:
            return Response({'error': '无效的推荐码'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Distributor binding failed: {str(e)}")
            return Response({'error': '绑定失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)