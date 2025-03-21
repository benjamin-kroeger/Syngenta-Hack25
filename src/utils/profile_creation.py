import json


def write_user(name: str, longitude: float, latitude: float, crops: list[str], applied_biologicals: list[str] = None):
    if applied_biologicals is None:
        applied_biologicals = []

    with open("user.json", "w") as f:
        json.dump({"name": name, "longitude": longitude, "latitude": latitude, "crops": [c.lower() for c in crops],
                   "applied_biologicals": applied_biologicals}, f,
                  indent=4)


def get_user_info():
    with open("user.json", "r") as f:
        return json.load(f)


if __name__ == "__main__":
    write_user(
        name="<NAME>",
        longitude=-97.0,
        latitude=37.0,
        crops=["hi"]
    )
