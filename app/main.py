from enum import auto
from typing import Union, Optional, List
from fastapi.params import Body
from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange

import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models, schemas, utils
from .database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from .routers import post, users

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

app.include_router(post.router)
app.include_router(users.router)
