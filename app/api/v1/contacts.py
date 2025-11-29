from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api import deps
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.crud import crud_user

# Оголошення
router = APIRouter()


# 1. GET (Read All)
@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(deps.get_db)
):
    contacts = await crud_user.get_users(db, skip=skip, limit=limit)
    return contacts


# 2. POST (Create)
@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: ContactCreate, db: AsyncSession = Depends(deps.get_db)):
    # Тут можна додати перевірку, чи існує вже такий email
    return await crud_user.create_user(db, user_in)


# 3. GET (Read One)
@router.get("/{user_id}", response_model=ContactResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(deps.get_db)):
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Contact not found")
    return user


# 4. PATCH (Update) - використовуємо PATCH для часткового оновлення
@router.patch("/{user_id}", response_model=ContactResponse)
async def update_user(
    user_id: int, contact_update: ContactUpdate, db: AsyncSession = Depends(deps.get_db)
):
    contact = await crud_user.update_user(db, user_id, contact_update)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


# 5. DELETE
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(deps.get_db)):
    user = await crud_user.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Contact not found")

    # При 204 Content ми нічого не повертаємо (return None)
