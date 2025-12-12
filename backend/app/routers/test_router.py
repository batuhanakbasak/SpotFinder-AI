from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
def say_hello():
    print("Endpoint is working")  
    return {"message": "Hello SpotFinder!"}


# app/routers/users_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from infrastructure.repositories.user_repository import UserRepository
from services.user_service import UserService
from schemas.user_schema import UserCreateSchema

router = APIRouter()

@router.post("/add", tags=["users"])
def add_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    service = UserService(repo)
    created_user = service.create_user(user.plate, user.country)
    if not created_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return {
        "message": "User added successfully",
        "user": {"plate": created_user.plate, "country": created_user.country}
    }