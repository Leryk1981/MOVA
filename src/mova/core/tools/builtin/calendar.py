"""
Calendar tool for MOVA SDK
Інструмент календаря для MOVA SDK
"""

from typing import Dict, Any
from ..base import BaseTool


class CalendarTool(BaseTool):
    """Інструмент для роботи з календарем"""
    
    def __init__(self):
        schema = {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "Ім'я клієнта"
                },
                "service": {
                    "type": "string",
                    "description": "Послуга, яка надається"
                },
                "start_time": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Час початку послуги у форматі ISO 8601"
                },
                "duration_min": {
                    "type": "integer",
                    "minimum": 15,
                    "maximum": 240,
                    "description": "Тривалість послуги в хвилинах"
                },
                "notes": {
                    "type": "string",
                    "description": "Додаткові нотатки"
                }
            },
            "required": ["customer_name", "service", "start_time"]
        }
        
        super().__init__(
            name="calendar.create_event",
            description="Create an appointment in the calendar",
            schema=schema
        )
    
    def run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Створити подію в календарі"""
        try:
            # В реальному проекті тут був би код для інтеграції з календарним сервісом
            # Наприклад, Google Calendar, Outlook, тощо
            
            customer_name = args.get("customer_name")
            service = args.get("service")
            start_time = args.get("start_time")
            duration_min = args.get("duration_min", 60)
            notes = args.get("notes", "")
            
            # Симуляція створення події
            event_id = f"event_{hash(customer_name + service + start_time) % 10000}"
            
            return {
                "success": True,
                "event_id": event_id,
                "message": f"Created appointment for {customer_name} at {start_time} for {service}",
                "details": {
                    "customer_name": customer_name,
                    "service": service,
                    "start_time": start_time,
                    "duration_min": duration_min,
                    "notes": notes
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }