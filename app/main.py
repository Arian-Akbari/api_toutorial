from fastapi import FastAPI
from pydantic import BaseModel
from . import models
from .database import engine
from .routers import post, users, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


app.include_router(post.router)
app.include_router(users.router)
app.include_router(auth.router)
