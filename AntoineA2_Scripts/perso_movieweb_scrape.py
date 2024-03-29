import os,sys
import json
import operator as op
import functools
import enum

import pickle

import dotenv

import requests
import urllib.parse

import dataclasses
from typing import Optional,List,Union

import watchmode_csv_parser


dotenv.load_dotenv(os.path.join(os.path.dirname(__file__),'.env'))

import unicodedata
from unidecode import unidecode

def clean_string(input_string):
    # Remove non-ASCII characters
    #ascii_string = ''.join(char for char in input_string if ord(char) < 128)
    ascii_string = unidecode(input_string)
    # Remove apostrophes
    cleaned_string = ascii_string.translate(str.maketrans('', '', "'"))
    
    return cleaned_string


def get_imdb_data(imdb_id):
    # Create directory if it doesn't exist
    directory = "IMDBot_responses"
    # if not os.path.exists(directory):
    #     os.makedirs(directory)

    # Check if data is already cached
    cache_file = os.path.join(directory, f"{imdb_id}.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)

    # If data is not cached, make a GET request
    url = f"https://search.imdbot.workers.dev/?tt={imdb_id}"
    response = requests.get(url)
    data = response.json()

    # Save response to cache file
    with open(cache_file, 'w') as f:
        json.dump(data, f)

    return data


class TMDB_API_MODE(enum.Enum):
    TMDB_ID = 1
    IMDB_ID = 2
    QUERY_STR = 3
     
def get_tmdb_details(**named_query_arg):
    
    if 'tmdb_id' in named_query_arg:
        api_mode = TMDB_API_MODE.TMDB_ID
        tmdb_id = named_query_arg['tmdb_id']
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?language=en-US"
        
    elif 'imdb_id' in named_query_arg:
        api_mode = TMDB_API_MODE.IMDB_ID
        imdb_id = named_query_arg['imdb_id']
        url = f"https://api.themoviedb.org/3/find/{imdb_id}?external_source=imdb_id"
        
        
    elif 'query' in named_query_arg:
        api_mode = TMDB_API_MODE.QUERY_STR
        #? Could try with different encodings
        encoded_query = urllib.parse.quote(named_query_arg['query']) 
        url = f"https://api.themoviedb.org/3/search/movie?query={encoded_query}&include_adult=true&language=en-US&page=1"

    else:
        raise KeyError(f"Cant request to TMDB: Need to use 'tmdb_id', 'imdb_id' or 'query' in {named_query_arg}")
    
    it = iter(map(os.environ.get,['tmdb_access_token', 'tmdb_api_key']))
    while (auth_key := next(it,None)) is not None:
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {auth_key}"
        }
        
        if api_mode == TMDB_API_MODE.TMDB_ID and \
                        os.path.exists((cache_file := os.path.join("TMDBapi_responses", f"{tmdb_id}.json"))):
            with open(cache_file, 'r') as f:
                    return json.load(f)
       
        response = requests.get(url, headers=headers)
        
        if api_mode == TMDB_API_MODE.TMDB_ID:
            
            data = response.json()
            with open(cache_file, 'w') as f:
                json.dump(data, f)
                
            return data
            
        elif api_mode == TMDB_API_MODE.IMDB_ID:
            
            movie = response.json().get('movie_results')[0]
            
            # data.setdefault('imdb_id',imdb_id)
            return get_tmdb_details(tmdb_id=movie['id'])
        
        elif api_mode == TMDB_API_MODE.QUERY_STR:
            
            #? Could try checking other results and/or pages
            movie = response.json().get('results')[0]
            
            return get_tmdb_details(tmdb_id=movie['id'])
            
        else:
            raise NameError("Bad API mode... Error in implementation")
    
    raise PermissionError("Could not do any successful requests to TMDB api")
    
def get_tmdb_keywords(tmdb_id):

    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/keywords"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.environ.get('tmdb_access_token')}"
    }

    response = requests.get(url, headers=headers)

    
    return list(response.json()['keywords'])


def get_tmdb_contentratings(tmdb_id,*, 
                            country_shortcodes= ['US', 'GB', 'IN', 'CA', 'JP', 'AU', 'DE', 'BR']):

    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/release_dates"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.environ.get('tmdb_access_token')}"
    }

    response = requests.get(url, headers=headers)

    
    # Function to filter entries based on country shortcode
    filter_country = functools.partial(filter, lambda entry: entry.get('iso_3166_1') in country_shortcodes)

    # Filtered entries
    filtered_entries = filter_country(response.json()['results'])

    return filtered_entries

def get_tmdb_cast_and_crew(tmdb_id,*,TOP_NUM_ACTORS=5,MAX_NUM_CREATORS=9,MAX_NUM_DIRECTORS=9):
    
    def filter_unique_crew(crew, department):
        unique_names = set()
        unique_entries = []
        for entry in crew:
            if entry['department'] == department and entry['name'] not in unique_names:
                unique_names.add(entry['name'])
                unique_entries.append(entry)
        return unique_entries
    
    def filter_unique_actors(actors_data):
        nonlocal TOP_NUM_ACTORS
        
        unique_names = set()
        unique_actors = []
        extra_actor = None
        for actor in actors_data:
            if actor['name'] not in unique_names:
                unique_names.add(actor['name'])
                unique_actors.append(actor)
            elif extra_actor is None:
                extra_actor = actor
        if len(unique_actors) < TOP_NUM_ACTORS and extra_actor is not None:
            unique_actors.append(extra_actor)
        return unique_actors[:TOP_NUM_ACTORS]
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits?language=en-US"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.environ.get('tmdb_access_token')}"
    }

    response = requests.get(url, headers=headers)

    response_json = response.json()
    
    crew_data = response_json['crew']
    
    unique_creators = filter_unique_crew(crew_data, 'Writing')[:MAX_NUM_CREATORS]
    unique_directors = filter_unique_crew(crew_data, 'Directing')[:MAX_NUM_DIRECTORS]
    
    cast_data =  list(response_json['cast'])
    
    unique_actors = filter_unique_actors(cast_data)
    
    return {'actors' : unique_actors, 'directors' : unique_directors , 'creators': unique_creators }

@dataclasses.dataclass
class MovieActorEntity:
    person_name : str
    character_name : str

@dataclasses.dataclass
class ContentRatingEntity:
    certificate : str
    country_shortcode : str
    
@dataclasses.dataclass
class CountryEntity:
    fullname : str
    shortcode : str

@dataclasses.dataclass(unsafe_hash=False,frozen=False)
class ParsedMovieEntity:
    tmdb_id : int #
    imdb_id : Union[str,None] #
    title : str #
    plot : str #
    content_rating : List[ContentRatingEntity] #
    rating : float
    release_year : int #
    AKA : str #
    num_reviews : int #
    runtime_minutes : int #A
    watchmode_id : Union[int,None] #


    actors : List[MovieActorEntity]
    directors : List[str]
    creators : List[str]
    genres : List[str] #
    langs : List[str]
    keywords : List[str] #
    countries : List[CountryEntity]
    
    @classmethod
    def from_json_imdbot(cls,resp):
        
        parsed = {}
        
        imdb_id = resp['imdbId']
        assert imdb_id != 'null'
        
        watchmode_ix = watchmode_csv_parser.watchmode_csvdict['imdb_id'] \
                                    .index(imdb_id)
                                    
        watchmode_id,tmdb_id, tmdb_type,w_title, w_year = \
        map(op.itemgetter(watchmode_ix),
                op.itemgetter('watchmode_id','tmdb_id','tmdb_type','title','year')(
                    watchmode_csv_parser.watchmode_csvdict
                )
        )
        
        parsed['imdb_id'] = imdb_id
        parsed['watchmode_id'] = int(watchmode_id)
        parsed['tmdb_id'] = int(tmdb_id)
        
        parsed['release_year'] = int(resp['main']['releaseYear']['year'])
        assert parsed['release_year'] == int(w_year)
        
        parsed['title'] = resp['main']['titleText']['text']
        
        parsed['plot'] = resp['top']['plot']['plotText']['plainText']
        #assert parsed['plot'] == resp['short']['description']
        
        parsed['num_reviews'] = int(resp['main']['reviews']['total'])
        
        parsed['runtime_minutes'] = int(resp['main']['runtime']['seconds']) // 60
        
        #TODO Use resp['main']['akas'] list edge-nodes instead ? 
        parsed['AKA'] = resp['fake']['#AKA']
        
        #TODO percent_rating from TMDB
        
        parsed['content_rating'] = resp['top']['certificate']['rating']
        #assert parsed['content_rating'] == resp['short']['contentRating']
        
        
        parsed['genres'] = list(
                                map(op.itemgetter('text'),
                                    resp['top']['genres']['genres']
                                    )
                                )
        
        parsed['keywords'] = list(
                                map(
                                    lambda el: el['node']['text'],
                                    resp['top']['keywords']['edges']
                                )
        )
        
        parsed['langs'] = None
        return cls(**parsed)
    
    
    @classmethod
    def CACHED_from_json_tmdb_queries(cls,api_response):
        tmdb_id = api_response.get("id", None)
        cache_dir = "TMDB_Dataclasses_cached"
        cache_file = os.path.join(cache_dir, f"{tmdb_id}.pkl")

        # Check if cached data exists
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                cached_data = pickle.load(f)
            return cached_data

        # Extract data and create ParsedMovieEntity object
        parsed_movie_entity = cls.from_json_tmdb_queries(api_response)

        # Cache the data
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_file, "wb") as f:
            pickle.dump(parsed_movie_entity, f)
            
        return parsed_movie_entity
    
    
    @classmethod
    def from_json_tmdb_queries(cls,api_response):

        tmdb_id = api_response.get("id", None)
        imdb_id = api_response.get("imdb_id", None)
        title = clean_string(api_response.get("title", ""))
        plot = clean_string(api_response.get("overview", ""))
        
        release_and_content_response = get_tmdb_contentratings(tmdb_id)
        content_rating = [ContentRatingEntity(entry['release_dates'][0]['certification'],
                                              entry['iso_3166_1']) 
                          for entry in release_and_content_response if entry['release_dates']
                        ]
        content_rating = list(filter(lambda cr_entity: cr_entity.certificate != "" ,
                                     content_rating)
                              )
         
        rating = api_response.get("vote_average", 0.0) * 10.00
        release_year = int(api_response.get("release_date", "").split('-')[0]) if api_response.get("release_date", None) else 0
        AKA = clean_string(api_response.get("original_title", "")) #! TEMP; use movie-alternative-titles 
        num_reviews = api_response.get("vote_count", 0)
        runtime_minutes = api_response.get("runtime", 0)
        
        watchmode_ix = watchmode_csv_parser.watchmode_csvdict['tmdb_id'] \
                            .index(str(tmdb_id))
        watchmode_id = watchmode_csv_parser.watchmode_csvdict['watchmode_id'][watchmode_ix]  

        
        cast_and_crew_response = get_tmdb_cast_and_crew(tmdb_id)
        actors = [MovieActorEntity(clean_string(actor['name']), clean_string(actor['character'])) for actor in cast_and_crew_response['actors']]  
        directors = [clean_string(director['name']) for director in cast_and_crew_response['directors']]  
        creators = [clean_string(creator['name']) for creator in cast_and_crew_response['creators']]   
        
        
        genres = [clean_string(genre['name']) for genre in api_response.get('genres', [])]
        langs = [clean_string(lang['name']) for lang in api_response.get('spoken_languages', [])] #! Spoken or use api translations ? 
        
        keywords_api_response = map(op.itemgetter("name"),get_tmdb_keywords(tmdb_id))
        keywords = list(map(clean_string,keywords_api_response) )
        
        countries = [CountryEntity(clean_string(name['name']), name['iso_3166_1']) for name in api_response.get('production_countries', [])]

        # Creating and returning a ParsedMovieEntity object
        return cls(
            tmdb_id=tmdb_id,
            imdb_id=imdb_id,
            title=title,
            plot=plot,
            content_rating=content_rating,
            rating=rating,
            release_year=release_year,
            AKA=AKA,
            num_reviews=num_reviews,
            runtime_minutes=runtime_minutes,
            watchmode_id=watchmode_id,
            actors=actors,
            directors=directors,
            creators=creators,
            genres=genres,
            langs=langs,
            keywords=keywords,
            countries=countries
        )





if __name__ == '__main__':
    
    # #! TEST 1
    # imdb_id1 = "tt0068646"
    
    # imdb_id2 = "tt1630029"
    # result1 = get_imdb_data(imdb_id2)

    
    # print(json.dumps(result1, indent=4))
    
    
    #! TEST 2
    if False:
        tmdb_id2 = "76600"
        
        result2 = get_tmdb_details(tmdb_id = tmdb_id2)
        
        print(json.dumps(result2, indent=4))
        
        parsed2 = ParsedMovieEntity.CACHED_from_json_tmdb_queries(result2)
        
        
        print(json.dumps(dataclasses.asdict(parsed2), indent=4))

    tmdb_ids = [37168, 69766, 597, 278, 238, 155, 13, 27205, 603, 680, 550, 769,41277, 274, 424, 857, 122, 120, 121, 98, 197, 329, 8587, 862, 12, 19995, 24428, 284054, 671, 672, 673, 674, 675, 767, 12444, 12445, 11, 1891, 1892, 1893, 1894, 1895, 218, 280, 135397, 351286, 49026, 324857, 109445, 330457, 420817, 9806, 661352, 301528, 127380, 157336]



    # tmdb_ids_dict = dict()
    # movies_list = [
    #     "La Guerre des tuques","La Grande Séduction", "Les voisins",
    # "Titanic", "The Shawshank Redemption", "The Godfather", "The Dark Knight", "Forrest Gump",
    # "Inception", "The Matrix", "Pulp Fiction", "Fight Club", "Goodfellas",
    # "The Silence of the Lambs", "Schindler's List", "Saving Private Ryan", "The Lord of the Rings: The Return of the King",
    # "The Lord of the Rings: The Fellowship of the Ring", "The Lord of the Rings: The Two Towers", "Gladiator", "Braveheart",
    # "Jurassic Park", "The Lion King", "Toy Story", "Finding Nemo", "Avatar",
    # "The Avengers", "Black Panther", "Harry Potter and the Sorcerer's Stone", "Harry Potter and the Chamber of Secrets",
    # "Harry Potter and the Prisoner of Azkaban", "Harry Potter and the Goblet of Fire", "Harry Potter and the Order of the Phoenix",
    # "Harry Potter and the Half-Blood Prince", "Harry Potter and the Deathly Hallows - Part 1", "Harry Potter and the Deathly Hallows - Part 2",
    # "Star Wars: Episode IV - A New Hope", "Star Wars: Episode V - The Empire Strikes Back", "Star Wars: Episode VI - Return of the Jedi",
    # "Star Wars: Episode I - The Phantom Menace", "Star Wars: Episode II - Attack of the Clones", "Star Wars: Episode III - Revenge of the Sith",
    # "The Terminator", "Terminator 2: Judgment Day", "Jurassic World", "Jurassic World: Fallen Kingdom", "The Dark Knight Rises",
    # "Spider-Man: Into the Spider-Verse", "The Lion King (2019)", "Frozen", "Frozen II", "Aladdin (2019)",
    # "The Incredibles", "The Incredibles 2", "Toy Story 4", "Finding Dory", "Interstellar"
    #     ]
    # for movie_query in movies_list:
    #     try:
    #         res = get_tmdb_details(query=movie_query)
    #         tmdb_ids_dict[movie_query] = res.get('id',None)
    #     except Exception as err:
    #         print(err)
    #         print(f"Error happened when trying to find: {movie_query}")
    #         print()
    #         tmdb_ids_dict[movie_query] = None
    #         continue
    
    # print(json.dumps(tmdb_ids_dict, indent=4))        
    # print(list(filter(None,tmdb_ids_dict.values())))
    
    pass

# {
#   "adult": false,
#   "backdrop_path": "/8rpDcsfLJypbO6vREc0547VKqEv.jpg",
#   "belongs_to_collection": {
#     "id": 87096,
#     "name": "Avatar Collection",
#     "poster_path": "/uO2yU3QiGHvVp0L5e5IatTVRkYk.jpg",
#     "backdrop_path": "/gxnvX9kF7RRUQYvB52dMLPgeJkt.jpg"
#   },
#   "budget": 460000000,
#   "genres": [
#     {
#       "id": 878,
#       "name": "Science Fiction"
#     },
#     {
#       "id": 12,
#       "name": "Adventure"
#     },
#     {
#       "id": 28,
#       "name": "Action"
#     }
#   ],
#   "homepage": "https://www.avatar.com/movies/avatar-the-way-of-water",
#   "id": 76600,
#   "imdb_id": "tt1630029",
#   "original_language": "en",
#   "original_title": "Avatar: The Way of Water",
#   "overview": "Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#   "popularity": 284.385,
#   "poster_path": "/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg",
#   "production_companies": [
#     {
#       "id": 127928,
#       "logo_path": "/h0rjX5vjW5r8yEnUBStFarjcLT4.png",
#       "name": "20th Century Studios",
#       "origin_country": "US"
#     },
#     {
#       "id": 574,
#       "logo_path": "/nLNW1TeFUYU0M5U0qmYUzOIwlB6.png",
#       "name": "Lightstorm Entertainment",
#       "origin_country": "US"
#     }
#   ],
#   "production_countries": [
#     {
#       "iso_3166_1": "US",
#       "name": "United States of America"
#     }
#   ],
#   "release_date": "2022-12-14",
#   "revenue": 2320250281,
#   "runtime": 192,
#   "spoken_languages": [
#     {
#       "english_name": "English",
#       "iso_639_1": "en",
#       "name": "English"
#     }
#   ],
#   "status": "Released",
#   "tagline": "Return to Pandora.",
#   "title": "Avatar: The Way of Water",
#   "video": false,
#   "vote_average": 7.6,
#   "vote_count": 11068
# }
