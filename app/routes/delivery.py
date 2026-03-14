from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Customer, Delivery, Vehicle

router = APIRouter(prefix="/api/deliveries", tags=["deliveries"])


class DeliveryCreate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = "pending"
    customer_id: int
    vehicle_id: Optional[int] = None


class DeliveryUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    customer_id: Optional[int] = None
    vehicle_id: Optional[int] = None


class DeliveryResponse(BaseModel):
    id: int
    description: Optional[str] = None
    status: str
    customer_id: int
    vehicle_id: Optional[int] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[DeliveryResponse])
def list_deliveries(db: Session = Depends(get_db)):
    deliveries = db.query(Delivery).all()
    return deliveries


@router.post("/", response_model=DeliveryResponse, status_code=201)
def create_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == delivery.customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    if delivery.vehicle_id is not None:
        vehicle = db.query(Vehicle).filter(Vehicle.id == delivery.vehicle_id).first()
        if vehicle is None:
            raise HTTPException(status_code=404, detail="Vehicle not found")
    db_delivery = Delivery(**delivery.model_dump())
    db.add(db_delivery)
    try:
        db.commit()
        db.refresh(db_delivery)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating delivery")
    return db_delivery


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(delivery_id: int, db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.put("/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(delivery_id: int, delivery: DeliveryUpdate, db: Session = Depends(get_db)):
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if db_delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    if delivery.customer_id is not None:
        customer = db.query(Customer).filter(Customer.id == delivery.customer_id).first()
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")
    if delivery.vehicle_id is not None:
        vehicle = db.query(Vehicle).filter(Vehicle.id == delivery.vehicle_id).first()
        if vehicle is None:
            raise HTTPException(status_code=404, detail="Vehicle not found")
    update_data = delivery.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_delivery, key, value)
    try:
        db.commit()
        db.refresh(db_delivery)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating delivery")
    return db_delivery


@router.delete("/{delivery_id}", status_code=204)
def delete_delivery(delivery_id: int, db: Session = Depends(get_db)):
    db_delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if db_delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    db.delete(db_delivery)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting delivery")
