"""
HTTP client for MOVA SDK
HTTP клієнт для MOVA SDK
"""

import asyncio
import aiohttp
import requests
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin
from loguru import logger

from .config import get_config_value
from .cache import cached


class MovaHTTPClient:
    """
    HTTP client for MOVA API integrations
    HTTP клієнт для інтеграцій MOVA API
    """
    
    def __init__(self, base_url: str = "", headers: Optional[Dict[str, str]] = None):
        """
        Initialize HTTP client
        Ініціалізація HTTP клієнта
        
        Args:
            base_url: Base URL for API / Базовий URL для API
            headers: Default headers / За замовчуванням заголовки
        """
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.timeout = get_config_value("api_timeout", 30)
        self.retries = get_config_value("api_retries", 3)
        self.session = None
    
    def _get_full_url(self, endpoint: str) -> str:
        """Get full URL from endpoint / Отримати повний URL з кінцевої точки"""
        if endpoint.startswith('http'):
            return endpoint
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare headers for request / Підготувати заголовки для запиту"""
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        return request_headers
    
    @cached(ttl=300)  # Cache API responses for 5 minutes
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make GET request
        Виконати GET запит
        
        Args:
            endpoint: API endpoint / API кінцева точка
            params: Query parameters / Параметри запиту
            headers: Request headers / Заголовки запиту
            
        Returns:
            Response data / Дані відповіді
        """
        url = self._get_full_url(endpoint)
        request_headers = self._prepare_headers(headers)
        
        for attempt in range(self.retries):
            try:
                response = requests.get(
                    url, 
                    params=params, 
                    headers=request_headers, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                logger.debug(f"GET {url} - Status: {response.status_code}")
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"GET request failed (attempt {attempt + 1}/{self.retries}): {e}")
                if attempt == self.retries - 1:
                    raise
                continue
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             json_data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make POST request
        Виконати POST запит
        
        Args:
            endpoint: API endpoint / API кінцева точка
            data: Form data / Дані форми
            json_data: JSON data / JSON дані
            headers: Request headers / Заголовки запиту
            
        Returns:
            Response data / Дані відповіді
        """
        url = self._get_full_url(endpoint)
        request_headers = self._prepare_headers(headers)
        
        for attempt in range(self.retries):
            try:
                response = requests.post(
                    url,
                    data=data,
                    json=json_data,
                    headers=request_headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                logger.debug(f"POST {url} - Status: {response.status_code}")
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"POST request failed (attempt {attempt + 1}/{self.retries}): {e}")
                if attempt == self.retries - 1:
                    raise
                continue
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make PUT request
        Виконати PUT запит
        
        Args:
            endpoint: API endpoint / API кінцева точка
            data: Form data / Дані форми
            json_data: JSON data / JSON дані
            headers: Request headers / Заголовки запиту
            
        Returns:
            Response data / Дані відповіді
        """
        url = self._get_full_url(endpoint)
        request_headers = self._prepare_headers(headers)
        
        for attempt in range(self.retries):
            try:
                response = requests.put(
                    url,
                    data=data,
                    json=json_data,
                    headers=request_headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                logger.debug(f"PUT {url} - Status: {response.status_code}")
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"PUT request failed (attempt {attempt + 1}/{self.retries}): {e}")
                if attempt == self.retries - 1:
                    raise
                continue
    
    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make DELETE request
        Виконати DELETE запит
        
        Args:
            endpoint: API endpoint / API кінцева точка
            headers: Request headers / Заголовки запиту
            
        Returns:
            Response data / Дані відповіді
        """
        url = self._get_full_url(endpoint)
        request_headers = self._prepare_headers(headers)
        
        for attempt in range(self.retries):
            try:
                response = requests.delete(
                    url,
                    headers=request_headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                logger.debug(f"DELETE {url} - Status: {response.status_code}")
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"DELETE request failed (attempt {attempt + 1}/{self.retries}): {e}")
                if attempt == self.retries - 1:
                    raise
                continue


class AsyncMovaHTTPClient:
    """
    Async HTTP client for MOVA API integrations
    Асинхронний HTTP клієнт для інтеграцій MOVA API
    """
    
    def __init__(self, base_url: str = "", headers: Optional[Dict[str, str]] = None):
        """
        Initialize async HTTP client
        Ініціалізація асинхронного HTTP клієнта
        
        Args:
            base_url: Base URL for API / Базовий URL для API
            headers: Default headers / За замовчуванням заголовки
        """
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.timeout = aiohttp.ClientTimeout(total=get_config_value("api_timeout", 30))
        self.retries = get_config_value("api_retries", 3)
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry / Вхід асинхронного контекстного менеджера"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit / Вихід асинхронного контекстного менеджера"""
        if self.session:
            await self.session.close()
    
    def _get_full_url(self, endpoint: str) -> str:
        """Get full URL from endpoint / Отримати повний URL з кінцевої точки"""
        if endpoint.startswith('http'):
            return endpoint
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make async GET request
        Виконати асинхронний GET запит
        
        Args:
            endpoint: API endpoint / API кінцева точка
            params: Query parameters / Параметри запиту
            headers: Request headers / Заголовки запиту
            
        Returns:
            Response data / Дані відповіді
        """
        url = self._get_full_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        for attempt in range(self.retries):
            try:
                async with self.session.get(url, params=params, headers=request_headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    logger.debug(f"Async GET {url} - Status: {response.status}")
                    return data
                    
            except aiohttp.ClientError as e:
                logger.warning(f"Async GET request failed (attempt {attempt + 1}/{self.retries}): {e}")
                if attempt == self.retries - 1:
                    raise
                continue
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
                   json_data: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make async POST request
        Виконати асинхронний POST запит
        
        Args:
            endpoint: API endpoint / API кінцева точка
            data: Form data / Дані форми
            json_data: JSON data / JSON дані
            headers: Request headers / Заголовки запиту
            
        Returns:
            Response data / Дані відповіді
        """
        url = self._get_full_url(endpoint)
        request_headers = {**self.headers, **(headers or {})}
        
        for attempt in range(self.retries):
            try:
                async with self.session.post(url, data=data, json=json_data, headers=request_headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    logger.debug(f"Async POST {url} - Status: {response.status}")
                    return data
                    
            except aiohttp.ClientError as e:
                logger.warning(f"Async POST request failed (attempt {attempt + 1}/{self.retries}): {e}")
                if attempt == self.retries - 1:
                    raise
                continue


# Factory functions for creating clients
def create_http_client(base_url: str = "", headers: Optional[Dict[str, str]] = None) -> MovaHTTPClient:
    """Create synchronous HTTP client / Створити синхронний HTTP клієнт"""
    return MovaHTTPClient(base_url, headers)


def create_async_http_client(base_url: str = "", headers: Optional[Dict[str, str]] = None) -> AsyncMovaHTTPClient:
    """Create asynchronous HTTP client / Створити асинхронний HTTP клієнт"""
    return AsyncMovaHTTPClient(base_url, headers) 