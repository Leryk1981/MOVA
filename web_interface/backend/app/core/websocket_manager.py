"""
WebSocket Connection Manager
Менеджер WebSocket з'єднань
"""
from typing import Dict, List
from fastapi import WebSocket


class WebSocketManager:
    """Керування активними WebSocket з'єднаннями"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, List[str]] = {
            'dashboards': [],
            'widgets': [],
            'plugins': []
        }
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Підключити нового клієнта"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        """Відключити клієнта"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Видалити підписки клієнта
        for key in self.subscriptions:
            if client_id in self.subscriptions[key]:
                self.subscriptions[key].remove(client_id)
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Надіслати повідомлення конкретному клієнту"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: dict):
        """Розіслати повідомлення всім підключеним клієнтам"""
        for connection in self.active_connections.values():
            await connection.send_json(message)
    
    async def subscribe(self, client_id: str, subscription_type: str, item_id: str):
        """Підписати клієнта на оновлення"""
        subscription_key = f"{subscription_type}:{item_id}"
        if subscription_key not in self.subscriptions:
            self.subscriptions[subscription_key] = []
        if client_id not in self.subscriptions[subscription_key]:
            self.subscriptions[subscription_key].append(client_id)
    
    async def unsubscribe(self, client_id: str, subscription_type: str, item_id: str):
        """Відписати клієнта від оновлень"""
        subscription_key = f"{subscription_type}:{item_id}"
        if subscription_key in self.subscriptions and client_id in self.subscriptions[subscription_key]:
            self.subscriptions[subscription_key].remove(client_id)
    
    async def notify_subscribers(self, subscription_type: str, item_id: str, message: dict):
        """Сповістити підписаних клієнтів про зміни"""
        subscription_key = f"{subscription_type}:{item_id}"
        if subscription_key in self.subscriptions:
            for client_id in self.subscriptions[subscription_key]:
                await self.send_personal_message(message, client_id)



