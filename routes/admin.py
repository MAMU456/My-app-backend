from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import Admin, User, Product, Vendor
from schemas import AdminCreate, Token, ProductCreate, ProductResponse, UserResponse, VendorCreate, VendorResponse
from security import get_db, get_current_admin
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin"])

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_admin_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": username, "role": "admin", "exp": expire},
        SECRET_KEY, algorithm=ALGORITHM
    )

# ── Create first admin (run once, then protect or remove) ──
@router.post("/setup", response_model=Token)
def setup_admin(data: AdminCreate, db: Session = Depends(get_db)):
    existing = db.query(Admin).filter(Admin.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")
    admin = Admin(username=data.username, password=hash_password(data.password))
    db.add(admin)
    db.commit()
    token = create_admin_token(data.username)
    return {"access_token": token, "token_type": "bearer"}

# ── Admin Login ──
@router.post("/login", response_model=Token)
def admin_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == form_data.username).first()
    if not admin or not verify_password(form_data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    token = create_admin_token(admin.username)
    return {"access_token": token, "token_type": "bearer"}

# ── Product Management ──
@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    new_product = Product(name=product.name, description=product.description, price=product.price)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, updated: ProductCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.name = updated.name
    product.description = updated.description
    product.price = updated.price
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}

# ── User Management ──
@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(User).all()

@router.patch("/users/{user_id}/revoke")
def revoke_user(user_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": f"User {user.username} has been revoked"}

@router.patch("/users/{user_id}/restore")
def restore_user(user_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"message": f"User {user.username} has been restored"}

# ── Stats ──
@router.get("/stats")
def get_stats(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return {
        "total_users": db.query(User).count(),
        "active_users": db.query(User).filter(User.is_active == True).count(),
        "revoked_users": db.query(User).filter(User.is_active == False).count(),
        "total_products": db.query(Product).count(),
        "total_vendors": db.query(Vendor).count()
    }

# ── Vendor Management ──
@router.get("/vendors", response_model=List[VendorResponse])
def get_vendors(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return db.query(Vendor).all()

@router.post("/vendors", response_model=VendorResponse)
def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    new_vendor = Vendor(**vendor.dict())
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return new_vendor

@router.put("/vendors/{vendor_id}", response_model=VendorResponse)
def update_vendor(vendor_id: int, updated: VendorCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    for key, value in updated.dict().items():
        setattr(vendor, key, value)
    db.commit()
    db.refresh(vendor)
    return vendor

@router.delete("/vendors/{vendor_id}")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    db.delete(vendor)
    db.commit()
    return {"message": "Vendor deleted"}
