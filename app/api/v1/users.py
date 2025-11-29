# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.api import deps
# from app.schemas.user import UserCreate, UserResponse
# from app.crud import crud_user

# # Оголошення
# router = APIRouter()

# @router.post("/", response_model=UserResponse)
# async def create_user(
#     user_in: UserCreate,
#     db: AsyncSession = Depends(deps.get_db)
# ):
#     # Викликаємо CRUD, роутер сам нічого не пише в базу
#     return await crud_user.create(db, obj_in=user_in)
