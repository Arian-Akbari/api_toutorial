from .. import models, schemas, utils
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from ..database import engine, SessionLocal, get_db
from typing import Union, Optional, List
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM post""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO post(title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/posts/{ide}", response_model=schemas.Post)
def get_posts(ide: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * from post WHERE id = %s""", (str(ide),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == ide).first()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            , detail=f"post with id : {ide} was not found")
    return post


@router.delete("/posts/{ide}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(ide: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM post WHERE id = %s returning *""", (str(ide),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == ide)

    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id : {ide} not exist")

    post.delete(synchronize_session=False)
    db.commit()


@router.put("/posts/{ide}", response_model=schemas.Post)
def update_post(ide: int, updated_post: schemas.PostUpdate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE post SET title = %s , content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, str(ide)))
    #
    # update_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == ide)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id : {ide} not exist")
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()
