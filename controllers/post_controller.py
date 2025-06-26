
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from schemas.post_schema import PostCreate, PostUpdate
from services import post_service
from auth.bearer import jwtBearer, user_access, writer_access
from core.database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(writer_access)])
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(jwtBearer())
):
    return post_service.create_post(
        db=db,
        post_data=post,
        current_user_email=payload["userID"],
        current_user_role=payload["role"]
    )


@router.get("/{post_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(user_access)])
def get_post(post_id: int, db: Session = Depends(get_db)):
    return post_service.get_post_by_id(db, post_id)


@router.put("/{post_id}", status_code=status.HTTP_200_OK)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    return post_service.update_post(db, post_id, post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post_service.delete_post(db, post_id)
    return {"detail": "Post deleted successfully"}
