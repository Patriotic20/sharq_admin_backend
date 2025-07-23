from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import os
from fastapi import UploadFile, HTTPException, status
from uuid import uuid4
from src.service import ModelType
from typing import Type



async def save_uploaded_file(file: UploadFile, upload_dir: str | None = "uploads"):
    os.makedirs(upload_dir, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return file_path


async def save_file_path_to_db(
    db: AsyncSession,
    item_id: int,
    file_path: str,
    user_id: int,
    filed_name: str,
    model: Type[ModelType],
):
    stmt = select(model).where(model.user_id == user_id, model.id == item_id)
    result = await db.execute(stmt)
    user_data = result.scalars().first()

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi ma'lumoti topilmadi",
        )

    stmt_2 = update(model).where(model.id == item_id).values({filed_name: file_path})
    await db.execute(stmt_2)
    await db.commit()

    return {"status": "success", "file_path": file_path}




