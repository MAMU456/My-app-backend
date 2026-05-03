from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Vendor, VendorRating, Order
from security import get_db, get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/vendors", tags=["Ratings"])

class RatingCreate(BaseModel):
    rating: float

@router.post("/{vendor_id}/rate")
def rate_vendor(
    vendor_id: int,
    data: RatingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not (1 <= data.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    has_ordered = db.query(Order).filter(
        Order.user_id == current_user.id,
        Order.vendor_id == vendor_id
    ).first()
    if not has_ordered:
        raise HTTPException(status_code=403, detail="You can only rate vendors you have ordered from")

    existing = db.query(VendorRating).filter(
        VendorRating.user_id == current_user.id,
        VendorRating.vendor_id == vendor_id
    ).first()

    if existing:
        existing.rating = data.rating
    else:
        new_rating = VendorRating(
            user_id=current_user.id,
            vendor_id=vendor_id,
            rating=data.rating
        )
        db.add(new_rating)

    db.commit()

    avg = db.query(func.avg(VendorRating.rating)).filter(
        VendorRating.vendor_id == vendor_id
    ).scalar()
    count = db.query(VendorRating).filter(VendorRating.vendor_id == vendor_id).count()

    vendor.rating = round(avg, 1)
    vendor.rating_count = count
    db.commit()

    return {
        "message": "Rating submitted successfully",
        "new_rating": vendor.rating,
        "rating_count": vendor.rating_count
    }

@router.get("/{vendor_id}/my-rating")
def get_my_rating(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    rating = db.query(VendorRating).filter(
        VendorRating.user_id == current_user.id,
        VendorRating.vendor_id == vendor_id
    ).first()
    return {"rating": rating.rating if rating else None}
