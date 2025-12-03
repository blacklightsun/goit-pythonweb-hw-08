from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


# --- READ (Get All) ---
async def get_contacts(db: AsyncSession, skip: int = 0, limit: int = 10):
    # select(Contact) створює запит SELECT * FROM contacts
    stmt = select(Contact).offset(skip).limit(limit)
    result = await db.execute(stmt)
    # scalars().all() перетворює брудний результат SQL у список об'єктів Python
    return result.scalars().all()


# --- CREATE ---
async def create_contact(db: AsyncSession, contact_in: ContactCreate):
    stmt = select(Contact).where(
        (Contact.email.ilike(f"%{contact_in.email}%"))
        | (Contact.phone_number.ilike(f"%{contact_in.phone_number}%"))
    )
    result = await db.execute(stmt)
    existing_contacts = result.scalars().all()

    if existing_contacts:
        return None
        raise ValueError("Contact with this email or phone number already exists.")

    # Створюємо об'єкт моделі
    # Тут треба хешувати пароль, але для спрощення поки пишемо plain text
    db_contact = Contact(
        firstname=contact_in.firstname,
        lastname=contact_in.lastname,
        email=contact_in.email,
        phone_number=contact_in.phone_number,
        birthday=contact_in.birthday,
        other_details=contact_in.other_details,
        owner_id=contact_in.owner_id,
    )
    db.add(db_contact)
    await db.commit()  # Зберігаємо в БД
    await db.refresh(db_contact)  # Оновлюємо об'єкт (отримуємо ID, який видала база)
    return db_contact


# --- READ (Get By ID) ---
async def get_contact(db: AsyncSession, contact_id: int):
    # session.get - найшвидший спосіб отримати по Primary Key
    return await db.get(Contact, contact_id)


# --- UPDATE ---
async def update_contact(
    db: AsyncSession, contact_id: int, contact_update: ContactUpdate
):
    # Спочатку знаходимо об'єкт
    db_contact = await get_contact(db, contact_id)
    if not db_contact:
        return None

    # Оновлюємо тільки ті поля, які прийшли (exclude_unset=True)
    update_data = contact_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_contact, key, value)  # Оновлюємо атрибути об'єкта

    await db.commit()
    await db.refresh(db_contact)
    return db_contact


# --- DELETE ---
async def delete_contact(db: AsyncSession, contact_id: int):
    db_contact = await get_contact(db, contact_id)
    if not db_contact:
        return None

    await db.delete(db_contact)
    await db.commit()
    return db_contact


# --- READ (Get All by query) ---
async def get_contacts_by_query(
    db: AsyncSession, query: str, skip: int = 0, limit: int = 10
):
    stmt = (
        select(Contact)
        .where(
            (Contact.firstname.ilike(f"%{query}%"))
            | (Contact.lastname.ilike(f"%{query}%"))
            | (Contact.email.ilike(f"%{query}%"))
            | (Contact.phone_number.ilike(f"%{query}%"))
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


# --- READ (Get All Users) ---
async def get_contacts_by_birthdays(
    db: AsyncSession, days_ahead: int, skip: int = 0, limit: int = 10
):
    from datetime import datetime, timedelta

    today = datetime.today()
    end_date = today + timedelta(days=days_ahead)
    today_str = today.strftime("%m-%d")
    end_date_str = end_date.strftime("%m-%d")

    stmt = (
        select(Contact)
        .where(Contact.birthday >= today_str, Contact.birthday < end_date_str)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
