from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Company, Customer

router = APIRouter(prefix="/api/customers", tags=["customers"])


class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company_id: int


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company_id: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CustomerResponse])
def list_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return customers


@router.post("/", response_model=CustomerResponse, status_code=201)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == customer.company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    try:
        db.commit()
        db.refresh(db_customer)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating customer")
    return db_customer


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
