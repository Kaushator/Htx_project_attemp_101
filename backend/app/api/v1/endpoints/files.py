"""
File upload and processing endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from services.parser_csv import FileParser
from core.config import settings
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/files/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process CSV/XLSX file"""
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Save file to upload directory
        upload_path = Path(settings.UPLOAD_DIR)
        upload_path.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_path / file.filename
        
        # Read and save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File uploaded: {file.filename}")
        
        # Process file in background
        background_tasks.add_task(process_uploaded_file, str(file_path), db)
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "size": len(content),
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")


@router.get("/files/list")
async def list_files():
    """List uploaded files"""
    try:
        upload_path = Path(settings.UPLOAD_DIR)
        if not upload_path.exists():
            return {"files": []}
        
        files = []
        for file_path in upload_path.iterdir():
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
        
        return {"files": files}
        
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail="Failed to list files")


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete uploaded file"""
    try:
        file_path = Path(settings.UPLOAD_DIR) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path.unlink()
        logger.info(f"File deleted: {filename}")
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete file")


async def process_uploaded_file(file_path: str, db: AsyncSession):
    """Process uploaded file in background"""
    try:
        parser = FileParser()
        
        # Parse file based on extension
        if file_path.endswith('.csv'):
            data = await parser.parse_csv_file(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            data = await parser.parse_excel_file(file_path)
        else:
            logger.error(f"Unsupported file type: {file_path}")
            return
        
        # Save to database
        await parser.save_to_database(data, db)
        
        logger.info(f"File processed successfully: {file_path}")
        
    except Exception as e:
        logger.error(f"File processing failed: {e}")
