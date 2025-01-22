from django.conf import settings
import logging
import requests
from datetime import datetime

logger = logging.getLogger('notification')

class WeChatNotification:
    @staticmethod
    def send_template_message(openid, template_id, data, page=None):
        """发送微信模板消息"""
        try:
            url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={settings.WX_ACCESS_TOKEN}"
            
            message = {
                "touser": openid,
                "template_id": template_id,
                "data": data
            }
            if page:
                message["page"] = page
                
            response = requests.post(url, json=message)
            result = response.json()
            
            if result.get('errcode') == 0:
                logger.info(f"Template message sent successfully to {openid}")
                return True
            
            logger.error(f"Failed to send template message: {result}")
            return False
            
        except Exception as e:
            logger.error(f"Error sending template message: {str(e)}")
            return False

class NotificationService:
    @staticmethod
    def send_refund_notification(order, refund_amount, refund_reason):
        """发送退款通知"""
        try:
            # 给用户发送退款通知
            user_data = {
                "thing1": {"value": order.order_number},  # 订单编号
                "amount2": {"value": f"¥{refund_amount}"},  # 退款金额
                "thing3": {"value": refund_reason},  # 退款原因
                "date4": {"value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  # 退款时间
            }
            WeChatNotification.send_template_message(
                order.user.wechat_openid,
                settings.WX_REFUND_TEMPLATE_ID,
                user_data,
                f"/pages/order/detail?id={order.id}"
            )
            
            # 给分销商发送佣金变动通知
            if order.distributor:
                distributor_data = {
                    "thing1": {"value": "退款佣金扣除"},
                    "amount2": {"value": f"¥{order.commission_amount}"},
                    "thing3": {"value": f"订单{order.order_number}已退款"},
                    "date4": {"value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                }
                WeChatNotification.send_template_message(
                    order.distributor.wechat_openid,
                    settings.WX_COMMISSION_TEMPLATE_ID,
                    distributor_data,
                    f"/pages/distribution/order?id={order.id}"
                )
                
        except Exception as e:
            logger.error(f"Error sending refund notification: {str(e)}")