from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse


# --- READ (Get By ID) ---
async def get_contact(db: AsyncSession, contact_id: int):
    # session.get - найшвидший спосіб отримати по Primary Key
    return await db.get(Contact, contact_id)


# --- READ (Get All) ---
async def get_contacts(db: AsyncSession, skip: int = 0, limit: int = 10):
    # select(Contact) створює запит SELECT * FROM contacts
    stmt = select(Contact).offset(skip).limit(limit)
    result = await db.execute(stmt)
    # scalars().all() перетворює брудний результат SQL у список об'єктів Python
    return result.scalars().all()


# --- CREATE ---
async def create_contact(db: AsyncSession, contact_in: ContactCreate):
    # Створюємо об'єкт моделі
    # Тут треба хешувати пароль, але для спрощення поки пишемо plain text
    db_contact = Contact(
        username=contact_in.username,
        hashed_password=contact_in.password + "not_really_hashed",  # Імітація
        # role=contact_in.role
    )
    db.add(db_contact)
    await db.commit()  # Зберігаємо в БД
    await db.refresh(db_contact)  # Оновлюємо об'єкт (отримуємо ID, який видала база)
    return db_contact


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
