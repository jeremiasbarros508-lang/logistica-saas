from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Company, Vehicle

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


class VehicleCreate(BaseModel):
    plate: str
    model: str
    capacity: Optional[float] = None
    company_id: int


class VehicleUpdate(BaseModel):
    plate: Optional[str] = None
    model: Optional[str] = None
    capacity: Optional[float] = None
    company_id: Optional[int] = None


class VehicleResponse(BaseModel):
    id: int
    plate: str
    model: str
    capacity: Optional[float] = None
    company_id: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[VehicleResponse])
def list_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).all()
    return vehicles


@router.post("/", response_model=VehicleResponse, status_code=201)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == vehicle.company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    try:
        db.commit()
        db.refresh(db_vehicle)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating vehicle")
    return db_vehicle


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: int, vehicle: VehicleUpdate, db: Session = Depends(get_db)):
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.company_id is not None:
        company = db.query(Company).filter(Company.id == vehicle.company_id).first()
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
    update_data = vehicle.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_vehicle, key, value)
    try:
        db.commit()
        db.refresh(db_vehicle)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating vehicle")
    return db_vehicle


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(db_vehicle)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting vehicle")
