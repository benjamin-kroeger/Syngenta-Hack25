import json


def create_user(name: str, longitude: float, latitude: float, crops: list[str]):
    with open("user.json", "w") as f:
        json.dump({"name": name, "longitude": longitude, "latitude": latitude, "crops": crops}, f,indent=4)



if __name__ == "__main__":
    create_user(
        name="<NAME>",
        longitude=-97.0,
        latitude=37.0,
        crops=["hi"]
    )