from rest_framework.exceptions import APIException
from rest_framework import status

class PhoneVerificationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '手机验证失败'
    default_code = 'phone_verification_error'

class DistributorBindingError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '分销商绑定失败'
    default_code = 'distributor_binding_error'

class SMSError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = '短信发送失败'
    default_code = 'sms_error'