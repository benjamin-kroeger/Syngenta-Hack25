from fastapi import FastAPI
from src.api_interfaces.indicator_calculation import heat_stress
app = FastAPI()


@app.get("/")
async def get_all_alerts():
    return {"message": "hi"}