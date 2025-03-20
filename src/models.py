from pydantic import BaseModel, Field
from typing import List


class User(BaseModel):
    name: str = Field(..., description="User's name")
    longitude: float = Field(..., description="User's longitude location")
    latitude: float = Field(..., description="User's latitude location")
    crops: List[str] = Field(..., min_length=1, description="List of crops the user is growing (at least one required)")