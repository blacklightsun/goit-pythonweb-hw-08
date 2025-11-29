from pydantic import BaseModel, EmailStr, ConfigDict


class ContactCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    phone_number: str
    birthday: str  # Format: YYYY-MM-DD
    other_details: str


class ContactUpdate(ContactCreate):
    pass


class ContactResponse(ContactCreate):
    id: int

    # Цей конфіг дозволяє Pydantic читати дані прямо з ORM-об'єктів SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
