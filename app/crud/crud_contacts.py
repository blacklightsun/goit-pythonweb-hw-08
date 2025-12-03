# from ast import stmt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


# --- READ (Get All) ---
async def get_contacts(db: AsyncSession, skip: int = 0, limit: int = 10):
    stmt = select(Contact).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


# --- CREATE ---
async def create_contact(db: AsyncSession, contact_in: ContactCreate):
    """Створює новий контакт у базі даних"""
    if not await check_contact_email_exists(db, contact_in.email):
        return None

    if not await check_contact_phone_exists(db, contact_in.phone_number):
        return None

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
    return await db.get(Contact, contact_id)


# --- UPDATE ---
async def update_contact(
    db: AsyncSession, contact_id: int, contact_update: ContactUpdate
):
    # Спочатку знаходимо об'єкт
    db_contact = await get_contact(db, contact_id)
    if not db_contact:
        return None

    if contact_update.email:
        if not await check_contact_email_exists(db, contact_update.email):
            return None

    if contact_update.phone_number:
        if not await check_contact_phone_exists(db, contact_update.phone_number):
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
    from datetime import date, timedelta

    def is_birthday_within_next_seven_days(birthday_str):
        """Перевіряє, чи день народження (YYYY-MM-DD string) припадає на найближчі 7 днів."""
        # Перетворюємо рядок на об'єкт дати (використовуючи будь-який рік, наприклад, поточний)
        current_year = date.today().year
        # month_day = datetime.strptime(birthday_str, '%Y-%m-%d').replace(year=current_year).date()
        month_day = birthday_str.replace(year=current_year)

        today = date.today()
        seven_days_before = today - timedelta(days=days_ahead)

        return today >= month_day >= seven_days_before

    # Отримуємо всі контакти (або великий список) з бази даних
    all_contacts = await db.execute(select(Contact))

    # Фільтруємо в Python
    upcoming_birthdays = [
        contact
        for contact in all_contacts.scalars().all()
        if is_birthday_within_next_seven_days(contact.birthday)
    ]
    return upcoming_birthdays


async def check_contact_email_exists(db: AsyncSession, email: str | None) -> bool:
    stmt = select(Contact).where(Contact.email == email)
    result = await db.execute(stmt)
    contact = result.scalars().first()
    return contact is not None


async def check_contact_phone_exists(db: AsyncSession, phone: str | None) -> bool:
    stmt = select(Contact).where(Contact.phone_number == phone)
    result = await db.execute(stmt)
    contact = result.scalars().first()
    return contact is not None
