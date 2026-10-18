from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models  # noqa: F401  (registers all tables on Base.metadata)
from .database import Base, engine
from .routers import auth, billing, clinical, org, patients, ref


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Hospital Management System", lifespan=lifespan)

for r in (auth.router, ref.router, org.router, patients.router, clinical.router, billing.router):
    app.include_router(r)


@app.get("/")
def root():
    return {"status": "ok"}
