from typing import Union, Optional
from fastapi.params import Body
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models, schemas
from .database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
                                password='50598287', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('database connection was successfull')
        break
    except Exception as error:
        print(' connecting to database failed')
        print('Error: ', error)
        time.sleep(2)


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM post""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO post(title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {
        new_post
    }


@app.get("/sqlalch")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {
        posts
    }


@app.get("/posts/{ide}")
def get_posts(ide: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * from post WHERE id = %s""", (str(ide),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == ide).first()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            , detail=f"post with id : {ide} was not found")
    return {
        post
    }


@app.delete("/posts/{ide}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(ide: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM post WHERE id = %s returning *""", (str(ide),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == ide)

    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id : {ide} not exist")

    post.delete(synchronize_session=False)
    db.commit()


@app.put("/posts/{ide}")
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

    return {
        post_query.first()
    }
