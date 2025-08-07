"""
Utility functions for MOVA SDK
Утилітарні функції для MOVA SDK
"""

import re
import json
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from loguru import logger


def generate_id(prefix: str = "mova") -> str:
    """
    Generate unique identifier
    Згенерувати унікальний ідентифікатор
    
    Args:
        prefix: ID prefix / Префікс ID
        
    Returns:
        Unique ID / Унікальний ID
    """
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations
    Очистити назву файлу для безпечних операцій з файлами
    
    Args:
        filename: Original filename / Оригінальна назва файлу
        
    Returns:
        Sanitized filename / Очищена назва файлу
    """
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized


def format_timestamp(timestamp: Optional[Union[str, datetime]] = None, 
                    format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format timestamp to string
    Форматувати часову мітку в рядок
    
    Args:
        timestamp: Timestamp to format / Часову мітку для форматування
        format_str: Format string / Рядок формату
        
    Returns:
        Formatted timestamp / Відформатована часова мітка
    """
    if timestamp is None:
        timestamp = datetime.now()
    elif isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    return timestamp.strftime(format_str)


def parse_json_safe(data: str, default: Any = None) -> Any:
    """
    Safely parse JSON string
    Безпечно розпарсити JSON рядок
    
    Args:
        data: JSON string / JSON рядок
        default: Default value if parsing fails / Значення за замовчуванням при помилці
        
    Returns:
        Parsed data or default / Розпарсені дані або значення за замовчуванням
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default


def to_json_safe(data: Any, default: str = "{}") -> str:
    """
    Safely convert data to JSON string
    Безпечно конвертувати дані в JSON рядок
    
    Args:
        data: Data to convert / Дані для конвертації
        default: Default JSON string if conversion fails / JSON рядок за замовчуванням при помилці
        
    Returns:
        JSON string / JSON рядок
    """
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to convert to JSON: {e}")
        return default


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries
    Глибоке об'єднання двох словників
    
    Args:
        dict1: First dictionary / Перший словник
        dict2: Second dictionary / Другий словник
        
    Returns:
        Merged dictionary / Об'єднаний словник
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten nested dictionary
    Вирівняти вкладений словник
    
    Args:
        data: Dictionary to flatten / Словник для вирівнювання
        parent_key: Parent key prefix / Префікс батьківського ключа
        sep: Key separator / Роздільник ключів
        
    Returns:
        Flattened dictionary / Вирівняний словник
    """
    items = []
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(data: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """
    Unflatten dictionary with dot notation
    Розгорнути словник з точковою нотацією
    
    Args:
        data: Flattened dictionary / Вирівняний словник
        sep: Key separator / Роздільник ключів
        
    Returns:
        Nested dictionary / Вкладений словник
    """
    result = {}
    for key, value in data.items():
        keys = key.split(sep)
        current = result
        for k in keys[:-1]:
            current = current.setdefault(k, {})
        current[keys[-1]] = value
    return result


def validate_email(email: str) -> bool:
    """
    Validate email address format
    Валідувати формат email адреси
    
    Args:
        email: Email address to validate / Email адреса для валідації
        
    Returns:
        True if valid / True якщо валідна
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format
    Валідувати формат URL
    
    Args:
        url: URL to validate / URL для валідації
        
    Returns:
        True if valid / True якщо валідний
    """
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to specified length
    Обрізати текст до вказаної довжини
    
    Args:
        text: Text to truncate / Текст для обрізання
        max_length: Maximum length / Максимальна довжина
        suffix: Suffix to add if truncated / Суфікс для додавання при обрізанні
        
    Returns:
        Truncated text / Обрізаний текст
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_text_from_html(html: str) -> str:
    """
    Extract plain text from HTML
    Витягти звичайний текст з HTML
    
    Args:
        html: HTML content / HTML контент
        
    Returns:
        Plain text / Звичайний текст
    """
    # Simple HTML tag removal
    text = re.sub(r'<[^>]+>', '', html)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def calculate_hash(data: Union[str, bytes], algorithm: str = 'md5') -> str:
    """
    Calculate hash of data
    Обчислити хеш даних
    
    Args:
        data: Data to hash / Дані для хешування
        algorithm: Hash algorithm / Алгоритм хешування
        
    Returns:
        Hash string / Рядок хешу
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if algorithm == 'md5':
        return hashlib.md5(data).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(data).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(data).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists
    Забезпечити існування директорії
    
    Args:
        path: Directory path / Шлях до директорії
        
    Returns:
        Path object / Об'єкт Path
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes
    Отримати розмір файлу в байтах
    
    Args:
        file_path: Path to file / Шлях до файлу
        
    Returns:
        File size in bytes / Розмір файлу в байтах
    """
    return Path(file_path).stat().st_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    Форматувати розмір файлу в зручному для читання форматі
    
    Args:
        size_bytes: Size in bytes / Розмір в байтах
        
    Returns:
        Formatted size string / Відформатований рядок розміру
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def retry_on_exception(max_retries: int = 3, delay: float = 1.0, 
                      exceptions: tuple = (Exception,)):
    """
    Decorator for retrying functions on exception
    Декоратор для повторних спроб функцій при винятку
    
    Args:
        max_retries: Maximum number of retries / Максимальна кількість спроб
        delay: Delay between retries in seconds / Затримка між спробами в секундах
        exceptions: Exceptions to catch / Винятки для перехоплення
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                        import time
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed. Last error: {e}")
            raise last_exception
        return wrapper
    return decorator 