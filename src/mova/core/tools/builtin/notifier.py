"""
Notifier tool for MOVA SDK
Інструмент сповіщень для MOVA SDK
"""

from typing import Dict, Any
from ..base import BaseTool


class NotifierTool(BaseTool):
    """Інструмент для відправки сповіщень"""
    
    def __init__(self):
        schema = {
            "type": "object",
            "properties": {
                "phone": {
                    "type": "string",
                    "description": "Номер телефону для SMS"
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "Email адреса"
                },
                "message": {
                    "type": "string",
                    "maxLength": 200,
                    "description": "Текст повідомлення"
                },
                "notification_type": {
                    "type": "string",
                    "enum": ["sms", "email", "both"],
                    "default": "sms",
                    "description": "Тип сповіщення"
                }
            },
            "required": ["message"],
            "anyOf": [
                {"required": ["phone"]},
                {"required": ["email"]}
            ]
        }
        
        super().__init__(
            name="notifier.send_notification",
            description="Send SMS or email notification",
            schema=schema
        )
    
    def run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Відправити сповіщення"""
        try:
            # В реальному проекті тут був би код для інтеграції з SMS/email сервісами
            
            phone = args.get("phone")
            email = args.get("email")
            message = args.get("message")
            notification_type = args.get("notification_type", "sms")
            
            results = {}
            
            # Відправка SMS
            if phone and notification_type in ["sms", "both"]:
                # Симуляція відправки SMS
                sms_id = f"sms_{hash(phone + message) % 10000}"
                results["sms"] = {
                    "success": True,
                    "message_id": sms_id,
                    "recipient": phone
                }
            
            # Відправка Email
            if email and notification_type in ["email", "both"]:
                # Симуляція відправки Email
                email_id = f"email_{hash(email + message) % 10000}"
                results["email"] = {
                    "success": True,
                    "message_id": email_id,
                    "recipient": email
                }
            
            return {
                "success": True,
                "message": f"Notification sent via {notification_type}",
                "details": {
                    "notification_type": notification_type,
                    "message": message,
                    "results": results
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }