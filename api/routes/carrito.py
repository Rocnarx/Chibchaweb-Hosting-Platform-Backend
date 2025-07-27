from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from api.database import SessionLocal
import uuid

router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

