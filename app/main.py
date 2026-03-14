from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import models  # noqa: F401 – registers all ORM models with Base
from app.routes import company, customer, delivery, user, vehicle


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Logística SaaS API", version="1.0.0", lifespan=lifespan)

app.include_router(company.router)
app.include_router(customer.router)
app.include_router(delivery.router)
app.include_router(user.router)
app.include_router(vehicle.router)
