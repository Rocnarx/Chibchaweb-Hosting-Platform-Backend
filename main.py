from fastapi import FastAPI
from api.routes import router
from api.database import engine, Base
import api.models_sqlalchemy
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(router)

origins = [
    "http://localhost:5173",  # tu frontend local
    "https://tu-frontend-en-produccion.com",  # si lo subes después
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # o ["*"] para todos, solo para pruebas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)