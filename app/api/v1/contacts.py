from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api import deps
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.crud import crud_contacts

# Оголошення
router = APIRouter()


# 1. GET (Read All)
@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(deps.get_db)
):
    contacts = await crud_contacts.get_contacts(db, skip=skip, limit=limit)
    return contacts


# 2. POST (Create)
@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_in: ContactCreate, db: AsyncSession = Depends(deps.get_db)
):
    # Тут можна додати перевірку, чи існує вже такий email
    new_contact = await crud_contacts.create_contact(db, contact_in)
    if not new_contact:
        raise HTTPException(
            status_code=400,
            detail="Contact with this email or phone number already exists.",
        )
    return new_contact


# 3. GET (Read One)
@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: AsyncSession = Depends(deps.get_db)):
    contact = await crud_contacts.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


# 4. PATCH (Update) - використовуємо PATCH для часткового оновлення
@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: AsyncSession = Depends(deps.get_db),
):
    contact = await crud_contacts.update_contact(db, contact_id, contact_update)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


# 5. DELETE
@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(deps.get_db)):
    contact = await crud_contacts.delete_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    # При 204 Content ми нічого не повертаємо (return None)
    return None


# 6. GET (Read All with query parameters)
@router.get("/{query}", response_model=List[ContactResponse])
async def read_contacts_by_query(
    query: str, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(deps.get_db)
):
    contacts = await crud_contacts.get_contacts_by_query(
        db, query, skip=skip, limit=limit
    )
    return contacts


# 7. GET (Read All birthdaays in next n days)
@router.get("/birthdays/{day}", response_model=List[ContactResponse])
async def read_contacts_for_birthdays(
    day: int, skip: int = 0, limit: int = 10, db: AsyncSession = Depends(deps.get_db)
):
    contacts = await crud_contacts.get_contacts_by_birthdays(
        db, day, skip=skip, limit=limit
    )
    return contacts
