from pydantic import BaseModel, Field
from typing import List


class User(BaseModel):
    name: str = Field(default="Ranjid", description="User's name")
    longitude: float = Field(default=75, description="User's longitude location")
    latitude: float = Field(default=25, description="User's latitude location")
    crops: List[str] = Field(default=["cotton","Wheat"], min_length=1, description="List of crops the user is growing (at least one required)")

class BiologicalApplication(BaseModel):
    biological: str = Field(default="stress_buster", description="The name of the biological")
    crop : str = Field(default="cotton", description="The name of the crop")
    issue:str = Field(default="night_heat_stress", description="The name of the issue")