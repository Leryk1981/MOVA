"""
CRM tool for MOVA SDK
Інструмент CRM для MOVA SDK
"""

from typing import Dict, Any
from ..base import BaseTool


class CRMTool(BaseTool):
    """Інструмент для роботи з CRM системою"""
    
    def __init__(self):
        schema = {
            "type": "object",
            "properties": {
                "phone": {
                    "type": "string",
                    "description": "Номер телефону клієнта"
                },
                "name": {
                    "type": "string",
                    "description": "Ім'я клієнта"
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "Email клієнта"
                },
                "notes": {
                    "type": "string",
                    "description": "Нотатки про клієнта"
                },
                "preferences": {
                    "type": "object",
                    "description": "Переваги клієнта"
                }
            },
            "required": ["phone"]
        }
        
        super().__init__(
            name="crm.create_or_update_client",
            description="Upsert client profile in CRM",
            schema=schema
        )
    
    def run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Створити або оновити клієнта в CRM"""
        try:
            # В реальному проекті тут був би код для інтеграції з CRM системою
            
            phone = args.get("phone")
            name = args.get("name")
            email = args.get("email")
            notes = args.get("notes")
            preferences = args.get("preferences", {})
            
            # Симуляція створення/оновлення клієнта
            client_id = f"client_{hash(phone) % 10000}"
            is_new = True  # В реальному проекті тут була б перевірка чи існує клієнт
            
            return {
                "success": True,
                "client_id": client_id,
                "is_new": is_new,
                "message": f"{'Created' if is_new else 'Updated'} client profile for {name or phone}",
                "details": {
                    "phone": phone,
                    "name": name,
                    "email": email,
                    "notes": notes,
                    "preferences": preferences
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }