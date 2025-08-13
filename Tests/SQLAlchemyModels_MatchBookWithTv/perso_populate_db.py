import perso_movieweb_scrape
from perso_movieweb_scrape import *


def generate_insert_queries(parsed_movies):
    queries = []
    for movie in parsed_movies:
        # Insert into movie table
        movie_query = f"INSERT INTO movie (tmdb_id, imdb_id, title, plot, rating, release_year, AKA, num_reviews, runtime, watchmode_id) VALUES ({movie.tmdb_id}, '{movie.imdb_id}', '{movie.title}', '{movie.plot}', {movie.rating}, {movie.release_year}, '{movie.AKA}', {movie.num_reviews}, {movie.runtime_minutes}, {movie.watchmode_id});"
        queries.append(movie_query)
        
        # Insert into contentrating table
        for content_rating in movie.content_rating:
            content_rating_query = f"INSERT INTO contentrating (certificate, country_shortcode) VALUES ('{content_rating.certificate}', '{content_rating.country_shortcode}');"
            queries.append(content_rating_query)
        
        # Insert into movie_contentrating table
        for content_rating in movie.content_rating:
            movie_contentrating_query = f"INSERT INTO movie_contentrating (certificate_id, movie_id) SELECT certificate_id, {movie.tmdb_id} FROM contentrating WHERE certificate = '{content_rating.certificate}';"
            queries.append(movie_contentrating_query)
        
        # Insert into genre table
        for genre in movie.genres:
            genre_query = f"INSERT INTO genre (genre) VALUES ('{genre}');"
            queries.append(genre_query)
        
        # Insert into movie_genre table
        for genre in movie.genres:
            movie_genre_query = f"INSERT INTO movie_genre (genre_id, movie_id) SELECT genre_id, {movie.tmdb_id} FROM genre WHERE genre = '{genre}';"
            queries.append(movie_genre_query)
        
        # Insert into lang table
        for lang in movie.langs:
            lang_query = f"INSERT INTO lang (lang) VALUES ('{lang}');"
            queries.append(lang_query)
        
        # Insert into movie_lang table
        for lang in movie.langs:
            movie_lang_query = f"INSERT INTO movie_lang (lang_id, movie_id) SELECT lang_id, {movie.tmdb_id} FROM lang WHERE lang = '{lang}';"
            queries.append(movie_lang_query)
        
        # Insert into keyword table
        for keyword in movie.keywords:
            keyword_query = f"INSERT INTO keyword (keyword) VALUES ('{keyword}');"
            queries.append(keyword_query)
        
        # Insert into movie_keyword table
        for keyword in movie.keywords:
            movie_keyword_query = f"INSERT INTO movie_keyword (keyword_id, movie_id) SELECT keyword_id, {movie.tmdb_id} FROM keyword WHERE keyword = '{keyword}';"
            queries.append(movie_keyword_query)
        
        # Insert into country table
        for country in movie.countries:
            country_query = f"INSERT INTO country (fullname, shortcode) VALUES ('{country.fullname}', '{country.shortcode}');"
            queries.append(country_query)
        
        # Insert into movie_country table
        for country in movie.countries:
            movie_country_query = f"INSERT INTO movie_country (country_id, movie_id) SELECT country_id, {movie.tmdb_id} FROM country WHERE shortcode = '{country.shortcode}';"
            queries.append(movie_country_query)
        
        # Insert into person table for actors
        for actor in movie.actors:
            actor_query = f"INSERT INTO person (person_name) VALUES ('{actor.person_name}');"
            queries.append(actor_query)
        
        # Insert into actor table
        for actor in movie.actors:
            actor_query = f"INSERT INTO actor (person_id, movie_id, character_name) SELECT person_id, {movie.tmdb_id}, '{actor.character_name}' FROM person WHERE person_name = '{actor.person_name}';"
            queries.append(actor_query)
        
        # Insert into person table for directors and creators
        for director in movie.directors:
            director_query = f"INSERT INTO person (person_name) VALUES ('{director}');"
            queries.append(director_query)
        
        for creator in movie.creators:
            creator_query = f"INSERT INTO person (person_name) VALUES ('{creator}');"
            queries.append(creator_query)
        
        # Insert into director table
        for director in movie.directors:
            director_query = f"INSERT INTO director (person_id, movie_id) SELECT person_id, {movie.tmdb_id} FROM person WHERE person_name = '{director}';"
            queries.append(director_query)
        
        # Insert into creator table
        for creator in movie.creators:
            creator_query = f"INSERT INTO creator (person_id, movie_id) SELECT person_id, {movie.tmdb_id} FROM person WHERE person_name = '{creator}';"
            queries.append(creator_query)
    
    return queries

def generate_insert_queries2(parsed_movies,*,ignore_mode=True):
    QUERIES  = []
    FAILED_MOVIES = []
    _queries = []
    for movie in parsed_movies:
        try:
            # Insert into movie table
            movie_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO movie (tmdb_id, imdb_id, title, plot, rating, release_year, AKA, num_reviews, runtime, watchmode_id) VALUES ({movie.tmdb_id}, '{movie.imdb_id}', '{movie.title}', '{movie.plot}', {movie.rating}, {movie.release_year}, '{movie.AKA}', {movie.num_reviews}, {movie.runtime_minutes}, {movie.watchmode_id});"
            _queries.append(movie_query)
            
            # Insert into contentrating table
            for content_rating in movie.content_rating:
                content_rating_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO contentrating (certificate, country_shortcode) VALUES ('{content_rating.certificate}', '{content_rating.country_shortcode}');"
                _queries.append(content_rating_query)
            
            # Insert into movie_contentrating table
            for content_rating in movie.content_rating:
                movie_contentrating_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO movie_contentrating (certificate_id, movie_id) SELECT certificate_id, movie.movie_id FROM contentrating, movie WHERE certificate = '{content_rating.certificate}' AND movie.tmdb_id = {movie.tmdb_id};"
                _queries.append(movie_contentrating_query)
            
            # Insert into genre table
            for genre in movie.genres:
                genre_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO genre (genre) VALUES ('{genre}');"
                _queries.append(genre_query)
            
            # Insert into movie_genre table
            for genre in movie.genres:
                movie_genre_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO movie_genre (genre_id, movie_id) SELECT genre_id, movie.movie_id FROM genre, movie WHERE genre = '{genre}' AND movie.tmdb_id = {movie.tmdb_id};"
                _queries.append(movie_genre_query)
            
            # Insert into lang table
            for lang in movie.langs:
                lang_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO lang (lang) VALUES ('{lang}');"
                _queries.append(lang_query)
            
            # Insert into movie_lang table
            for lang in movie.langs:
                movie_lang_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO movie_lang (lang_id, movie_id) SELECT lang_id, movie.movie_id FROM lang, movie WHERE lang = '{lang}' AND movie.tmdb_id = {movie.tmdb_id};"
                _queries.append(movie_lang_query)
            
            # Insert into keyword table
            for keyword in movie.keywords:
                keyword_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO keyword (keyword) VALUES ('{keyword}');"
                _queries.append(keyword_query)
            
            # Insert into movie_keyword table
            for keyword in movie.keywords:
                movie_keyword_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO movie_keyword (keyword_id, movie_id) SELECT keyword_id, movie.movie_id FROM keyword, movie WHERE keyword = '{keyword}' AND movie.tmdb_id = {movie.tmdb_id};"
                _queries.append(movie_keyword_query)
            
            # Insert into country table
            for country in movie.countries:
                country_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO country (fullname, shortcode) VALUES ('{country.fullname}', '{country.shortcode}');"
                _queries.append(country_query)
            
            # Insert into movie_country table
            for country in movie.countries:
                movie_country_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO movie_country (country_id, movie_id) SELECT country_id, movie.movie_id FROM country, movie WHERE shortcode = '{country.shortcode}' AND movie.tmdb_id = {movie.tmdb_id};"
                _queries.append(movie_country_query)
            
            # Insert into person table for actors
            for actor in movie.actors:
                actor_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO person (person_name) VALUES ('{actor.person_name}');"
                _queries.append(actor_query)
            
            # Insert into actor table
            for actor in movie.actors:
                actor_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO actor (person_id, movie_id, character_name) SELECT person_id, movie.movie_id, '{actor.character_name}' FROM person, movie WHERE person_name = '{actor.person_name}' AND movie.tmdb_id = {movie.tmdb_id};"
                _queries.append(actor_query)
            
            # Insert into person table for directors and creators
            for director in movie.directors:
                director_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO person (person_name) VALUES ('{director}');"
                _queries.append(director_query)
            
            for creator in movie.creators:
                creator_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO person (person_name) VALUES ('{creator}');"
                _queries.append(creator_query)
            
            # Insert into director table
            for director in movie.directors:
                director_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO director (person_id, movie_id) SELECT person_id, movie.movie_id FROM person, movie WHERE person_name = '{director}' AND movie.tmdb_id = {movie.tmdb_id};"
                _queries.append(director_query)
            
            # Insert into creator table
            for creator in movie.creators:
                creator_query = f"INSERT {'IGNORE ' if ignore_mode else ''}INTO creator (person_id, movie_id) SELECT person_id, movie.movie_id FROM person, movie WHERE person_name = '{creator}' AND movie.tmdb_id = {movie.tmdb_id};"
                _queries.append(creator_query)

            _queries.append("\n\n")
        except Exception as err:
            FAILED_MOVIES.append(f"{movie.title} ({movie.tmdb_id})")
            print(*_queries,sep="\n")
            input(f"{movie.title} ({movie.tmdb_id}) : {err}\n")
            _queries.clear()
        else:
            QUERIES.extend(_queries.copy())
            _queries.clear()

    return QUERIES


example_movie = ParsedMovieEntity(
    tmdb_id=123456,  # Example TMDB ID
    imdb_id=None,    # Setting IMDb ID to None
    title="Example Movie",
    plot="This is an example plot.",
    content_rating=[ContentRatingEntity(certificate="PG-13", country_shortcode="US")],
    rating=7.5,
    release_year=2022,
    AKA="Alternate Title",
    num_reviews=1000,
    runtime_minutes=120,
    watchmode_id=789,  # Example Watchmode ID
    actors=[
        MovieActorEntity(person_name="John Doe", character_name="Hero"),
        MovieActorEntity(person_name="Jane Smith", character_name="Villain")
    ],
    directors=["Director One", "Director Two"],
    creators=["Creator One", "Creator Two"],
    genres=["Action", "Adventure"],
    langs=["English", "Francais"],
    keywords=["Example", "Keywords"],
    countries=[CountryEntity(fullname="United States", shortcode="US")]
)

parsed_movies = [example_movie]

it = iter(parsed_movies)
while (movie := next(it,None)) is not None :
    insert_queries = generate_insert_queries2([movie],ignore_mode=True)

    # input(f"{movie.title} ({movie.tmdb_id})\n")

    output_file = "DMLV4.sql"
    with open(output_file, "w+") as f:
        f.write("\n".join(insert_queries))

# TMDB_IDS_LIST = [37168, 69766, 597, 278, 238, 155, 13, 27205, 603, 680, 550, 769,41277, 274, 424, 857, 122, 120, 121, 98, 197, 329, 8587, 862, 12, 19995, 24428, 284054, 671, 672, 673, 674, 675, 767, 12444, 12445, 11, 1891, 1892, 1893, 1894, 1895, 218, 280, 135397, 351286, 49026, 324857, 109445, 330457, 420817, 9806, 661352, 301528, 127380, 157336]

# parsed_movies = list(map(lambda tmdb_id: ParsedMovieEntity.CACHED_from_json_tmdb_queries(
#     get_tmdb_details(tmdb_id = str(tmdb_id))),TMDB_IDS_LIST ))

# it = iter(parsed_movies)
# while (movie := next(it,None)) is not None :
#     insert_queries = generate_insert_queries2([movie],ignore_mode=True)

#     # input(f"{movie.title} ({movie.tmdb_id})\n")

#     output_file = "DMLV3.sql"
#     with open(output_file, "a+") as f:
#         f.write("\n".join(insert_queries))