from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from app.api.router import router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

