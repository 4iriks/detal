from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models after Base is declared so Alembic autogenerate sees metadata.
from app import models  # noqa: E402,F401
