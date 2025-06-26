# app/controllers/user_controller.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.user_schema import UserCreate, UserLogin, UserRoleUpdate
from services import user_service
from auth.jwt_handler import signJwt
from auth.bearer import admin_access
from core.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    new_user = user_service.create_user(db, user)
    return {"message": "User created successfully", "user_id": new_user.id}


@router.post("/login", status_code=status.HTTP_200_OK)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_email_and_password(db, user.email, user.password)
    return signJwt(db_user.email, db_user.role)


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user_by_id(db, user_id)


@router.put("/{user_id}/role", dependencies=[Depends(admin_access)], status_code=status.HTTP_200_OK)
def update_user_role(user_id: int, role_data: UserRoleUpdate, db: Session = Depends(get_db)):
    updated_user = user_service.update_user_role(db, user_id, role_data.role)
    return {"message": "User role updated successfully", "user_id": updated_user.id, "role": updated_user.role}
