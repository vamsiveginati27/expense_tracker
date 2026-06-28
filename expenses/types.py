from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=6, max_length=128)
    email: Optional[EmailStr] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "securepass123",
                "email": "john@example.com",
            }
        }


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

    class Config:
        json_schema_extra = {"example": {"username": "john_doe", "password": "securepass123"}}


class ExpenseRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0, le=1000000)
    category: str = Field(default="Other", max_length=50)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    class Config:
        json_schema_extra = {
            "example": {"description": "Lunch at restaurant", "amount": 25.50, "category": "Food"}
        }


class ExpenseUpdateRequest(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=200)
    amount: Optional[float] = Field(None, gt=0, le=1000000)
    category: Optional[str] = Field(None, max_length=50)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    class Config:
        json_schema_extra = {
            "example": {"description": "Updated description", "amount": 30.00, "category": "Dining"}
        }


class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    created_at: str


class ExpenseResponse(BaseModel):
    id: str
    user: str
    description: str
    amount: float
    category: str
    date: str
    created_at: str


class LoginResponse(BaseModel):
    message: str
    access_token: str
    user: UserResponse
