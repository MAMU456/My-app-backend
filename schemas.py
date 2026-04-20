from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    class Config:
        from_attributes = True

class AdminCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    class Config:
        from_attributes = True

class VendorCreate(BaseModel):
    name: str
    location: str
    hours: str
    phone: str
    email: str
    rating: float = 5.0
    status: str = "open"
    initials: str

class VendorResponse(BaseModel):
    id: int
    name: str
    location: str
    hours: str
    phone: str
    email: str
    rating: float
    status: str
    initials: str
    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    vendor_id: int
    delivery_address: str
    phone: str
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    id: int
    product_name: str
    product_price: float
    quantity: int
    subtotal: float
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    vendor_id: int
    delivery_address: str
    phone: str
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]
    class Config:
        from_attributes = True

class OrderAdminResponse(BaseModel):
    id: int
    vendor_id: int
    delivery_address: str
    phone: str
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]
    username: Optional[str] = None
    vendor_name: Optional[str] = None
    class Config:
        from_attributes = True
