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


@app.get("/")  # @ means decorator
def root():
    return {"data": "HELLO WORLD"}


@app.get("/posts", response_model=List[schemas.Post])
def root(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s,%s,%s) RETURNING *""",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()

    # conn.commit()  # for commiting all the changes into db
    # title=post.title, content=post.content, published=post.published
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # Returning * like in sql
    return new_post


# id field is path parameter
@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    # t = str(id)
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (t,)
    #                )  # weird isse , is required otherwise will throw error digit above 10
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} not found")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"Post with {id} not found"}

    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts where id=%s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()  # to change anything on database
    post = db.query(models.Post).filter(models.Post.id == id)

    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} not found")

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):

    # cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s Returning *""",
    #                (post.title, post.content, post.published, str(id),))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} not found")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_users(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # Hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users/{id}",  response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id:{id} does not exist")

    return user
