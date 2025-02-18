import requests
import time
import json

with open("config.json", "r") as file:
    config = json.load(file)

API_KEY = config["API_KEY"]
BASE_URL = "https://api.themoviedb.org/3/genre/movie"

params = {
    "api_key": API_KEY,
    "sort_by": "popularity.desc",  # Sort by popularity
    "page": 1  # Start from page 1
}

all_movies = []

MAX_PAGES = 500  

for page in range(1, MAX_PAGES + 1):
    params["page"] = page
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}, stopping at page {page}")
        break
    
    data = response.json()
    
    if "results" in data:
        all_movies.extend(data["results"])
    else:
        break  
    
    print(f"Fetched page {page}")
    time.sleep(0.5)

print(f"Total movies fetched: {len(all_movies)}")

# print(all_movies)

with open("movie_details.json", "w") as f:
    json.dump(all_movies, f)
