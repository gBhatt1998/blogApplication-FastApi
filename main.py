
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from auth.jwt_handler import signJwt, decodeJwt
import models
from database import SessionLocal, engine
from  auth.bearer import jwtBearer ,RoleChecker, user_access, writer_access, admin_access

app = FastAPI()
# models.Base.metadata.create_all(bind=engine)
# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

class PostCreate(BaseModel):
    title: str
    content: str
    user_id: int

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    user_id: Optional[int] = None

class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "bekpark",
                "email": "help@bek.com",
                "password": "1324",
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "help@bek.com",
                "password": "1324"
            }
        }

class UserRoleUpdate(BaseModel):
    user_id: int
    role: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/users/signup",tags=["users"], status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: db_dependency):
    try:
        db_user = models.User(
            username=user.username,
            email=user.email,
            password=user.password,  
            role=models.Role.USER)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "User created successfully", "user_id": db_user.id}
    except IntegrityError:
    
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

@app.post("/users/login", tags=["users"], status_code=status.HTTP_200_OK)
async def login_user(user: UserLogin, db: db_dependency):

    db_user = db.query(models.User).filter(models.User.email == user.email, models.User.password == user.password).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return signJwt(db_user.email,db_user.role)

@app.get("/users/{user_id}",  tags=["users"],status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.post("/posts/", tags=["posts"], dependencies=[Depends(writer_access)], status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: db_dependency,payload: dict = Depends(jwtBearer())):
   
    try:

        if payload["role"] != "admin":
            user = db.query(models.User).filter(models.User.email == payload["userID"]).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            if post.user_id != user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create post for another user")

        db_post = models.Post(**post.dict())
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post
    except IntegrityError:
      
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id or database error")

@app.get("/posts/{post_id}", tags=["posts"], dependencies=[Depends(user_access)], status_code=status.HTTP_200_OK)
async def read_post(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

@app.delete("/posts/{post_id}",tags=["posts"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"detail": "Post deleted successfully"}

@app.put("/posts/{post_id}",tags=["posts"], status_code=status.HTTP_200_OK)
async def update_post(post_id: int, post: PostUpdate, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    try:
        for key, value in post.dict().items():
            if value is not None:
                setattr(db_post, key, value)
        db.commit()
        db.refresh(db_post)
        return db_post
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id or database error")
    

    # python -m venv env    .\env\Scripts\activate   uvicorn main:app --reload   

@app.put("/users/{user_id}/role", tags=["users"], dependencies=[Depends(admin_access)], status_code=status.HTTP_200_OK)
async def update_user_role(user_id: int, role_update: UserRoleUpdate, db: db_dependency):
    if role_update.role not in ["user", "writer", "admin"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    return {"message": "User role updated successfully", "user_id": user.id, "role": user.role}