# app/main.py

from fastapi import FastAPI
from core.database import Base, engine
from controllers import user_controller, post_controller

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(user_controller.router)
app.include_router(post_controller.router)
