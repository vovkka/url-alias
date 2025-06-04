from typing import Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from url_alias.db.model import BaseModel as SQLAlchemyBaseModel

ModelType = TypeVar("ModelType", bound=SQLAlchemyBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticBaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticBaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for repository with CRUD operations"""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get object by id"""
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get(self, **kwargs) -> Optional[ModelType]:
        """Get object by kwargs"""
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ModelType]:
        """Get all objects"""
        query = select(self.model)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create object"""
        db_obj = self.model(**obj_in.model_dump())
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Update object"""
        update_data = obj_in.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelType) -> None:
        """Delete object"""
        await self.session.delete(db_obj)
        await self.session.flush()

    async def exists(self, **kwargs) -> bool:
        """Check if object exists by kwargs"""
        result = await self.get(**kwargs)
        return result is not None

    async def update_by_kwargs(self, obj_in: UpdateSchemaType, **kwargs) -> Optional[ModelType]:
        """Update object by kwargs"""
        db_obj = await self.get(**kwargs)
        if db_obj:
            return await self.update(db_obj, obj_in)
        return None

    async def register(self, obj_in: CreateSchemaType) -> ModelType:
        """Create object if it doesn't exist"""
        criteria = obj_in.model_dump()
        if not await self.exists(**criteria):
            return await self.create(obj_in)
        return await self.get(**criteria)
