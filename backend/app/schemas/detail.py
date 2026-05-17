from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.category import CategoryRead
from app.schemas.supplier import SupplierRead
from app.schemas.warehouse import WarehouseRead


class DetailBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    article: str = Field(min_length=2, max_length=100)
    material: str | None = Field(default=None, max_length=100)
    weight: Decimal | None = Field(default=None, ge=0)
    price: Decimal = Field(ge=0)
    quantity: int = Field(default=0, ge=0)
    category_id: int = Field(gt=0)
    supplier_id: int | None = Field(default=None, gt=0)
    warehouse_id: int | None = Field(default=None, gt=0)

    @field_validator("name", "article", mode="before")
    @classmethod
    def validate_required_text(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        normalized = value.strip()
        if not normalized:
            raise ValueError("Поле не может быть пустым")
        return normalized

    @field_validator("material")
    @classmethod
    def normalize_material(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class DetailCreate(DetailBase):
    pass


class DetailUpdate(DetailBase):
    pass


class DetailPartialUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    article: str | None = Field(default=None, min_length=2, max_length=100)
    material: str | None = Field(default=None, max_length=100)
    weight: Decimal | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None, gt=0)
    supplier_id: int | None = Field(default=None, gt=0)
    warehouse_id: int | None = Field(default=None, gt=0)

    @field_validator("name", "article", mode="before")
    @classmethod
    def validate_required_text(cls, value: Any) -> Any:
        if value is None:
            return None
        if not isinstance(value, str):
            return value

        normalized = value.strip()
        if not normalized:
            raise ValueError("Поле не может быть пустым")
        return normalized

    @field_validator("name", "article", "price", "quantity", "category_id")
    @classmethod
    def reject_required_null(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Поле не может быть пустым")
        return value

    @field_validator("material")
    @classmethod
    def normalize_material(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class DetailQuantityUpdate(BaseModel):
    quantity: int = Field(ge=0)


class DetailRead(BaseModel):
    id: int
    name: str
    article: str
    material: str | None
    weight: Decimal | None
    price: Decimal
    quantity: int
    category_id: int
    supplier_id: int | None
    warehouse_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DetailReadFull(DetailRead):
    category: CategoryRead
    supplier: SupplierRead | None
    warehouse: WarehouseRead | None
