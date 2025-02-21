from neo4j import GraphDatabase
import json
from tqdm import tqdm

with open("config.json", "r") as file:
    config = json.load(file)

URI = config["NEO4J_URI"]
AUTH = (config["NEO4J_USER"], config["NEO4J_PASSWORD"])

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    
def reset_database():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database reset successfully!")
            
def add_movie(title, released, actors, directors, writers, description=None, genres=None):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            session.run("CREATE (m:Movie {title: $title, released: $released, description: $description})", title=title, released=released, description=description)
            # for actor in actors:
            #     session.run("MERGE (a:Person {name: $actor})", actor=actor)
            #     session.run("MATCH (a:Person {name: $actor}), (m:Movie {title: $title}) "
            #                 "MERGE (a)-[:ACTED_IN]->(m)", actor=actor, title=title)
                
            if actors:
                session.run("""UNWIND $actors AS actor
                            MERGE (a:Person {name: actor})
                            WITH a
                            MATCH (m:Movie {title: $title})
                            MERGE (a)-[:ACTED_IN]->(m)
                            MERGE (m)-[:HAS_ACTOR]->(a)""", actors=actors, title=title
                            )
                
            # for writer in writers:
            #     session.run("MERGE (w:Person {name: $writer})", writer=writer)
            #     session.run("MATCH (w:Person {name: $writer}), (m:Movie {title: $title}) "
            #                 "MERGE (w)-[:WROTE]->(m)", writer=writer, title=title)
                
            if writers:
                session.run("""UNWIND $writers AS writer
                            MERGE (w:Person {name: writer})
                            WITH w
                            MATCH (m:Movie {title: $title})
                            MERGE (w)-[:WROTE]->(m)
                            MERGE (m)-[:HAS_WRITER]->(w)""", writers=writers, title=title
                            )
            
            # for director in directors:
            #     session.run("MERGE (d:Person {name: $director})", director=director)
            #     session.run("MATCH (d:Person {name: $director}), (m:Movie {title: $title}) "
            #                 "MERGE (d)-[:DIRECTED]->(m)", director=director, title=title)
            
            if directors:
                session.run("""UNWIND $directors AS director
                            MERGE (d:Person {name: director})
                            WITH d
                            MATCH (m:Movie {title: $title})
                            MERGE (d)-[:DIRECTED]->(m)
                            MERGE (m)-[:HAS_DIRECTOR]->(d)""", directors=directors, title=title
                            )
                
            # for genre in genres:
            #     session.run("MERGE (g:Genre {name: $genre})", genre=genre)
            #     session.run("MATCH (g:Genre {name: $genre}), (m:Movie {title: $title}) "
            #                 "MERGE (m)-[:IN_GENRE]->(g)", genre=genre, title=title)
            
            if genres:
                session.run("""UNWIND $genres AS genre
                            MERGE (g:Genre {name: genre})
                            WITH g
                            MATCH (m:Movie {title: $title})
                            MERGE (m)-[:IN_GENRE]->(g)
                            MERGE (g)-[:HAS_MOVIE]->(m)""", genres=genres, title=title
                            )
            
            # print("Movie added successfully!")
            
# add_movie("The Matrix", 1999, ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"], "Lana Wachowski", ["Lana Wachowski", "Lilly Wachowski"])
# add_movie("The Matrix Reloaded", 2003, ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"], "Lana Wachowski", ["Lana Wachowski", "Lilly Wachowski"])

def reverse_relation(title, released, actors, directors, writers, description=None, genres=None):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            session.run("""
                MERGE (m:Movie {title: $title}) 
                SET m.released = $released, m.description = $description
                
                FOREACH (actor IN $actors | 
                    MERGE (a:Person {name: actor}) 
                    MERGE (m)-[:HAS_ACTOR]->(a)
                )

                FOREACH (writer IN $writers | 
                    MERGE (w:Person {name: writer}) 
                    MERGE (m)-[:HAS_WRITER]->(w)
                )

                FOREACH (director IN $directors | 
                    MERGE (d:Person {name: director}) 
                    MERGE (m)-[:HAS_DIRECTOR]->(d)
                )

                FOREACH (genre IN $genres | 
                    MERGE (g:Genre {name: genre}) 
                    MERGE (g)-[:HAS_MOVIE]->(m)
                )
            """, 
            title=title, released=released, description=description,
            actors=actors or [], writers=writers or [], 
            directors=directors or [], genres=genres or []
            )

                
def add_reverse_relation():
    with open("genres.json", "r") as file:
        genres = json.load(file)
        
    with open("movie_details_with_credits.json", "r") as file:
        movies = json.load(file)
        for i, movie in enumerate(tqdm(movies)):
            title = movie["title"]
            released = movie["release_date"].split("-")[0]
            actors = movie["actors"]
            directors = movie["director"]
            writers = movie["writer"]
            description = movie["overview"]
            genre_ids = movie["genre_ids"]
            genres_list = [genre["name"] for genre in genres if genre["id"] in genre_ids]
            
            reverse_relation(title, released, actors, directors, writers, description, genres_list)

def add_movies():
    with open("genres.json", "r") as file:
        genres = json.load(file)
        
    with open("movie_details_with_credits.json", "r") as file:
        movies = json.load(file)
    
    length_ = len(movies)
    movies = movies[:length_//2]
     
    for i, movie in enumerate(tqdm(movies)):
        title = movie["title"]
        released = movie["release_date"].split("-")[0]
        actors = movie["actors"]
        directors = movie["director"]
        writers = movie["writer"]
        description = movie["overview"]
        genre_ids = movie["genre_ids"]
        genres_list = [genre["name"] for genre in genres if genre["id"] in genre_ids]
        
        add_movie(title, released, actors, directors, writers, description, genres_list)
            
if __name__ == "__main__":
    args = input("Enter 'reset' to reset the database or 'add' to add movies: ")
    if args == "reset":
        reset_database()
    elif args == "add":
        add_movies()
    elif args == "reverse":
        add_reverse_relation()
    else:
        print("Invalid argument!")