from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class WeChatLoginSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    nickname = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.URLField(required=False, allow_blank=True)
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_parent_id(self, value):
        if value:
            try:
                parent = User.objects.get(id=value, role__in=[2, 3])
                return parent.id
            except User.DoesNotExist:
                raise serializers.ValidationError("无效的推荐人ID")
        return None

class WeChatUserSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'avatar', 'role', 
                 'balance', 'token', 'refresh']
        read_only_fields = fields
        class PhoneVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6)
    
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'avatar', 'phone']
        extra_kwargs = {
            'phone': {'required': False},
            'username': {'required': False},
            'avatar': {'required': False}
        }

class DistributorBindingSerializer(serializers.Serializer):
    parent_code = serializers.CharField(max_length=20)