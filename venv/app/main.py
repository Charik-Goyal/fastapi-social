from importlib.resources import contents
from random import randrange
from turtle import st
from typing import Optional, List
from fastapi import Body, Depends, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from .routers import post, user, auth

models.Base.metadata.create_all(bind=engine)

# database password charik123
app = FastAPI()  # instance


while True:
    try:
        conn = psycopg2.connect(
            host='localhost', database='fastapi', user='postgres', password='charik123', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database Connection is successful")
        break
    except Exception as error:
        print("Connecting to DB failed")
        print("Error: ", error)
        time.sleep(3)


my_posts = [{"title": "title of posts 1", "content": "content of posts 1", "id": 1},
            {"title": "favourite foods", "content": "i like pizza", "id": 2}]


def get_id(id):
    for p in my_posts:
        if (p['id'] == id):
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")  # @ means decorator
def root():
    return {"data": "HELLO WORLD"}
