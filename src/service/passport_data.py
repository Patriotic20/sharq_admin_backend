from fastapi import HTTPException, status
from src.service import BasicCrud
from sharq_models.models import PassportData, User #type: ignore
from src.schemas.passport_data import (
    PassportDataBase,
    PassportDataUpdate,
    PassportDataCreate,
)
from sqlalchemy.ext.asyncio import AsyncSession


class PassportDataCrud(BasicCrud[PassportData, PassportDataBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_passport_data(
        self, passport_data_item: PassportDataBase, user_id: int
    ):
        passport_data_with_user = PassportDataCreate(
            user_id=user_id, **passport_data_item.model_dump()
        )
        return await super().create(
            model=PassportData, obj_items=passport_data_with_user
        )

    async def get_passport_data_by_id(self, passport_data_id: int, user_id: int):
        passport_data_info: PassportData = await super().get_by_id(
            model=PassportData, item_id=passport_data_id
        )

        if not passport_data_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Passport data not found"
            )
        if passport_data_info.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authorized to access this resource",
            )

        return passport_data_info

    async def get_all_passport_data(
        self, limit: int = 20, offset: int = 0, current_user: User | None = None
    ):
        try:
            if current_user:
                return await super().get_all(
                    model=PassportData,
                    limit=limit,
                    offset=offset,
                    filters=[PassportData.user_id == current_user.id],
                )

            return await super().get_all(
                model=PassportData,
                limit=limit,
                offset=offset,
                filters=None,  # Optional, can be omitted
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve passport data records",
            ) from e

    async def update_passport_data(
        self,
        passport_data_id: int,
        update_items: PassportDataUpdate,
        user_id: int,
    ):
        await self.get_passport_data_by_id(
            passport_data_id=passport_data_id, user_id=user_id
        )
        return await super().update(
            model=PassportData, item_id=passport_data_id, obj_items=update_items
        )

    async def delete_passport_data(self, passport_data_id: int, user_id: int):
        await self.get_passport_data_by_id(
            passport_data_id=passport_data_id, user_id=user_id
        )
        return await super().delete(model=PassportData, item_id=passport_data_id)
