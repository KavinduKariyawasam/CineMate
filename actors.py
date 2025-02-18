import requests
import json
from tqdm import tqdm

with open("movie_details.json", "r") as f:
    movie_details = json.load(f)
    
with open("config.json", "r") as f:
    config = json.load(f)

API_KEY = config["API_KEY"]
    
# get id and get actor details, director details and writer details and dump to a file
for movie in tqdm(movie_details):
    movie_id = movie["id"]
    URL = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    
    response = requests.get(URL)
    
    if response.status_code == 200:
        movie_credits = response.json()
        crew = movie_credits["crew"]
        cast = movie_credits["cast"]
        
        writers = []
        for member in crew:
            if member["job"] == "Screenplay" or member["job"] == "Writer":
                writers.append(member["name"])
        if writers:
            movie["writer"] = writers
        else:
            movie["writer"] = None
        
        actors = []
        
        for member in cast:
            if member["known_for_department"] == "Acting":
                actors.append(member["name"])
        movie["actors"] = actors
        
        directors = []
        for member in crew:
            if member["job"] == "Director":
                directors.append(member["name"])
        if directors:
            movie["director"] = directors
        else:
            movie["director"] = None
        # movie["credits"] = movie_credits
    else:
        print(f"Error: {response.status_code} for movie {movie_id}")
        
    # print(f"Processed movie {movie_id}")
        
with open("movie_details_with_credits.json", "w", encoding="utf-8") as f:
    json.dump(movie_details, f, indent=4, ensure_ascii=False)