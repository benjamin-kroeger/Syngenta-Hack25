from fastapi import FastAPI
from fastapi import status
from src.models import User
from src.utils.profile_creation import create_user
app = FastAPI()


@app.get("/")
async def get_all_alerts():


    return {"message": "hi"}


@app.post("/users/create", status_code=status.HTTP_201_CREATED)
async def create_user_enntry(user: User):
    create_user(user.name, user.longitude, user.latitude, user.crops)
    return {"id",1}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

