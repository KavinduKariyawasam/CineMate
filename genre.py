import requests
import json

with open("config.json", "r") as file:
    config = json.load(file)

API_KEY = config["API_KEY"]
URL = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}"

response = requests.get(URL)

if response.status_code == 200:
    genres = response.json()["genres"]
    for genre in genres:
        print(f"ID: {genre['id']}, Name: {genre['name']}")
else:
    print("Error:", response.status_code)
    
with open("genres.json", "w") as f:
    json.dump(genres, f, indent=4)
