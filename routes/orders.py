from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Order, OrderItem, Product, Vendor
from schemas import OrderCreate, OrderResponse
from security import get_db, get_current_user
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse)
def place_order(order_data: OrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    vendor = db.query(Vendor).filter(Vendor.id == order_data.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    order_items = []
    total = 0.0

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        subtotal = product.price * item.quantity
        total += subtotal
        order_items.append(OrderItem(
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            quantity=item.quantity,
            subtotal=subtotal
        ))

    new_order = Order(
        user_id=current_user.id,
        vendor_id=order_data.vendor_id,
        delivery_address=order_data.delivery_address,
        phone=order_data.phone,
        total_price=total,
        status="pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in order_items:
        item.order_id = new_order.id
        db.add(item)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/my", response_model=List[OrderResponse])
def get_my_orders(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
