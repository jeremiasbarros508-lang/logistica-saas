from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import models  # noqa: F401 – registers all ORM models with Base
from app.routes import customer


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Logística SaaS API", version="1.0.0", lifespan=lifespan)

app.include_router(customer.router)
