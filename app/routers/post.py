from turtle import pos
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas, utils
from ..database import SessionLocal, engine, get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.Post])
def get_posts(
        db: Session = Depends(get_db),
        current_user: int = Depends(oauth2.get_current_user),
        limit: int = 10,
        skip: int = 0,
        search: Optional[str] = "",
):
    print(limit)
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
        post: schemas.PostCreate,
        db: Session = Depends(get_db),
        current_user: int = Depends(oauth2.get_current_user),
):
    new_post = models.Post(user_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{ide}", response_model=schemas.Post)
def get_posts(
        ide: int,
        db: Session = Depends(get_db),
        current_user: int = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == ide).first()
    print(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id : {ide} was not found",
        )
    return post


@router.delete("/{ide}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
        ide: int,
        db: Session = Depends(get_db),
        current_user: str = Depends(oauth2.get_current_user),
):
    post_querry = db.query(models.Post).filter(models.Post.id == ide)
    post = post_querry.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id : {ide} not exist",
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=" NOT Authorised to perform action",
        )
    post_querry.delete(synchronize_session=False)
    db.commit()


@router.put("/{ide}", response_model=schemas.Post)
def update_post(
        ide: int,
        updated_post: schemas.PostUpdate,
        db: Session = Depends(get_db),
        current_user: str = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == ide)
    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id : {ide} not exist",
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=" NOT Authorised to perform action",
        )
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()
