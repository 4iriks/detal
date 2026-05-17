from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WarehouseBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    address: str = Field(min_length=5, max_length=300)
    responsible_person: str | None = Field(default=None, max_length=150)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        normalized = value.strip()
        if not normalized:
            raise ValueError("Название склада не может быть пустым")
        return normalized

    @field_validator("address", mode="before")
    @classmethod
    def validate_address(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        normalized = value.strip()
        if not normalized:
            raise ValueError("Адрес склада не может быть пустым")
        return normalized

    @field_validator("responsible_person")
    @classmethod
    def normalize_responsible_person(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(WarehouseBase):
    pass


class WarehousePartialUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    address: str | None = Field(default=None, min_length=5, max_length=300)
    responsible_person: str | None = Field(default=None, max_length=150)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: Any) -> Any:
        if value is None:
            return None
        if not isinstance(value, str):
            return value

        normalized = value.strip()
        if not normalized:
            raise ValueError("Название склада не может быть пустым")
        return normalized

    @field_validator("name")
    @classmethod
    def reject_empty_name(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Название склада не может быть пустым")
        return value

    @field_validator("address", mode="before")
    @classmethod
    def validate_address(cls, value: Any) -> Any:
        if value is None:
            return None
        if not isinstance(value, str):
            return value

        normalized = value.strip()
        if not normalized:
            raise ValueError("Адрес склада не может быть пустым")
        return normalized

    @field_validator("address")
    @classmethod
    def reject_empty_address(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Адрес склада не может быть пустым")
        return value

    @field_validator("responsible_person")
    @classmethod
    def normalize_responsible_person(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class WarehouseRead(BaseModel):
    id: int
    name: str
    address: str
    responsible_person: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
