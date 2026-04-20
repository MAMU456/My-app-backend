from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import Vendor
from schemas import VendorResponse
from security import get_db
from typing import List

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.get("/", response_model=List[VendorResponse])
def get_all_vendors(db: Session = Depends(get_db)):
    return db.query(Vendor).all()
