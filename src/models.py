from pydantic import BaseModel, Field
from typing import List


class User(BaseModel):
    name: str = Field(default="Ranjid", description="User's name")
    longitude: float = Field(default=75, description="User's longitude location")
    latitude: float = Field(default=25, description="User's latitude location")
    crops: List[str] = Field(default=["Corn","Wheat"], min_length=1, description="List of crops the user is growing (at least one required)")