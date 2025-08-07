"""
File service for managing files
Сервіс для управління файлами
"""

import os
import shutil
import aiofiles
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..models.system import FileInfo, FileListResponse, FileUploadResponse
from ..core.config import settings


class FileService:
    """Сервіс для роботи з файлами"""
    
    def __init__(self):
        """Ініціалізація сервісу"""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Створюємо піддиректорії
        (self.upload_dir / "mova").mkdir(exist_ok=True)
        (self.upload_dir / "temp").mkdir(exist_ok=True)
        (self.upload_dir / "exports").mkdir(exist_ok=True)
    
    async def upload_file(self, file_content: bytes, filename: str, 
                         subdirectory: str = "mova") -> FileUploadResponse:
        """Завантаження файлу"""
        try:
            # Створюємо піддиректорію
            target_dir = self.upload_dir / subdirectory
            target_dir.mkdir(exist_ok=True)
            
            # Генеруємо унікальне ім'я файлу
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            
            file_path = target_dir / unique_filename
            
            # Зберігаємо файл
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            # Отримуємо інформацію про файл
            stat = file_path.stat()
            
            logger.info(f"File uploaded: {file_path} ({len(file_content)} bytes)")
            
            return FileUploadResponse(
                filename=unique_filename,
                size=len(file_content),
                path=str(file_path),
                uploaded_at=datetime.fromtimestamp(stat.st_mtime)
            )
        
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise
    
    async def list_files(self, directory: str = "mova", 
                        pattern: str = "*") -> FileListResponse:
        """Отримання списку файлів"""
        try:
            target_dir = self.upload_dir / directory
            
            if not target_dir.exists():
                return FileListResponse(files=[], total=0, directory=directory)
            
            files = []
            for file_path in target_dir.glob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "size": stat.st_size,
                        "type": file_path.suffix.lower(),
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "path": str(file_path)
                    })
            
            # Сортуємо за датою модифікації (новіші спочатку)
            files.sort(key=lambda x: x["modified"], reverse=True)
            
            return FileListResponse(
                files=files,
                total=len(files),
                directory=directory
            )
        
        except Exception as e:
            logger.error(f"File listing failed: {e}")
            raise
    
    async def get_file_info(self, filename: str, directory: str = "mova") -> Optional[FileInfo]:
        """Отримання інформації про файл"""
        try:
            file_path = self.upload_dir / directory / filename
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            return FileInfo(
                name=file_path.name,
                size=stat.st_size,
                type=file_path.suffix.lower(),
                modified=datetime.fromtimestamp(stat.st_mtime),
                path=str(file_path)
            )
        
        except Exception as e:
            logger.error(f"File info retrieval failed: {e}")
            return None
    
    async def read_file(self, filename: str, directory: str = "mova") -> Optional[str]:
        """Читання файлу"""
        try:
            file_path = self.upload_dir / directory / filename
            
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            return content
        
        except Exception as e:
            logger.error(f"File reading failed: {e}")
            return None
    
    async def write_file(self, filename: str, content: str, 
                        directory: str = "mova") -> bool:
        """Запис файлу"""
        try:
            target_dir = self.upload_dir / directory
            target_dir.mkdir(exist_ok=True)
            
            file_path = target_dir / filename
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            logger.info(f"File written: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"File writing failed: {e}")
            return False
    
    async def delete_file(self, filename: str, directory: str = "mova") -> bool:
        """Видалення файлу"""
        try:
            file_path = self.upload_dir / directory / filename
            
            if not file_path.exists():
                return False
            
            file_path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False
    
    async def copy_file(self, source_filename: str, target_filename: str,
                       source_directory: str = "mova", 
                       target_directory: str = "mova") -> bool:
        """Копіювання файлу"""
        try:
            source_path = self.upload_dir / source_directory / source_filename
            target_dir = self.upload_dir / target_directory
            target_dir.mkdir(exist_ok=True)
            target_path = target_dir / target_filename
            
            if not source_path.exists():
                return False
            
            shutil.copy2(source_path, target_path)
            logger.info(f"File copied: {source_path} -> {target_path}")
            return True
        
        except Exception as e:
            logger.error(f"File copying failed: {e}")
            return False
    
    async def move_file(self, source_filename: str, target_filename: str,
                       source_directory: str = "mova", 
                       target_directory: str = "mova") -> bool:
        """Переміщення файлу"""
        try:
            source_path = self.upload_dir / source_directory / source_filename
            target_dir = self.upload_dir / target_directory
            target_dir.mkdir(exist_ok=True)
            target_path = target_dir / target_filename
            
            if not source_path.exists():
                return False
            
            shutil.move(str(source_path), str(target_path))
            logger.info(f"File moved: {source_path} -> {target_path}")
            return True
        
        except Exception as e:
            logger.error(f"File moving failed: {e}")
            return False
    
    async def get_directory_size(self, directory: str = "mova") -> int:
        """Отримання розміру директорії"""
        try:
            target_dir = self.upload_dir / directory
            
            if not target_dir.exists():
                return 0
            
            total_size = 0
            for file_path in target_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size
        
        except Exception as e:
            logger.error(f"Directory size calculation failed: {e}")
            return 0
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Очищення тимчасових файлів"""
        try:
            temp_dir = self.upload_dir / "temp"
            if not temp_dir.exists():
                return 0
            
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            deleted_count = 0
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} temp files")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Temp files cleanup failed: {e}")
            return 0


# Глобальний екземпляр сервісу
file_service = FileService() 