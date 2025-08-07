"""
Files API routes
API роути для роботи з файлами
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List

from ..models.system import FileUploadResponse, FileListResponse, FileInfo
from ..models.common import ResponseModel, StatusEnum
from ..services.file_service import file_service

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    subdirectory: str = Form("mova")
):
    """Завантаження файлу"""
    try:
        content = await file.read()
        
        # Перевіряємо розмір файлу
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=413, detail="File too large")
        
        result = await file_service.upload_file(content, file.filename, subdirectory)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=FileListResponse)
async def list_files(
    directory: str = "mova",
    pattern: str = "*"
):
    """Отримання списку файлів"""
    try:
        return await file_service.list_files(directory, pattern)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{filename}")
async def get_file_info(
    filename: str,
    directory: str = "mova"
):
    """Отримання інформації про файл"""
    try:
        file_info = await file_service.get_file_info(filename, directory)
        
        if file_info is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="File info retrieved",
            data=file_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/read/{filename}")
async def read_file(
    filename: str,
    directory: str = "mova"
):
    """Читання файлу"""
    try:
        content = await file_service.read_file(filename, directory)
        
        if content is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="File content retrieved",
            data={"filename": filename, "content": content}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/write/{filename}")
async def write_file(
    filename: str,
    content: str,
    directory: str = "mova"
):
    """Запис файлу"""
    try:
        success = await file_service.write_file(filename, content, directory)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to write file")
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="File written successfully",
            data={"filename": filename}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{filename}")
async def delete_file(
    filename: str,
    directory: str = "mova"
):
    """Видалення файлу"""
    try:
        success = await file_service.delete_file(filename, directory)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="File deleted successfully",
            data={"filename": filename}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copy")
async def copy_file(
    source_filename: str,
    target_filename: str,
    source_directory: str = "mova",
    target_directory: str = "mova"
):
    """Копіювання файлу"""
    try:
        success = await file_service.copy_file(
            source_filename, target_filename,
            source_directory, target_directory
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Source file not found")
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="File copied successfully",
            data={
                "source": f"{source_directory}/{source_filename}",
                "target": f"{target_directory}/{target_filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/move")
async def move_file(
    source_filename: str,
    target_filename: str,
    source_directory: str = "mova",
    target_directory: str = "mova"
):
    """Переміщення файлу"""
    try:
        success = await file_service.move_file(
            source_filename, target_filename,
            source_directory, target_directory
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Source file not found")
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="File moved successfully",
            data={
                "source": f"{source_directory}/{source_filename}",
                "target": f"{target_directory}/{target_filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/directory/size")
async def get_directory_size(directory: str = "mova"):
    """Отримання розміру директорії"""
    try:
        size = await file_service.get_directory_size(directory)
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Directory size calculated",
            data={"directory": directory, "size_bytes": size}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup/temp")
async def cleanup_temp_files(max_age_hours: int = 24):
    """Очищення тимчасових файлів"""
    try:
        deleted_count = await file_service.cleanup_temp_files(max_age_hours)
        
        return ResponseModel(
            status=StatusEnum.SUCCESS,
            message="Temp files cleanup completed",
            data={"deleted_count": deleted_count, "max_age_hours": max_age_hours}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 