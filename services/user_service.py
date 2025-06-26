
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from models import User, Role
from schemas.user_schema import UserCreate, UserRoleUpdate


def create_user(db: Session, user_data: UserCreate) -> User:
    try:
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=Role.USER
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")


def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_user_by_email_and_password(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email, User.password == password).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return user


def update_user_role(db: Session, user_id: int, new_role: str) -> User:
    if new_role not in ["user", "writer", "admin"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = new_role
    db.commit()
    db.refresh(user)
    return user
