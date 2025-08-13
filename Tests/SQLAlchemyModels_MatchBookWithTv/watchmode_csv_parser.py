import os
import csv,json
import pickle

import operator as op

from collections import defaultdict

WATCHMODE_MAP_PATH = os.path.join(os.getcwd(),r"title_id_map.csv")
CACHE_FILE = os.path.join(os.getcwd(), r"watchmode_movie_dict.pkl")

def __main():

    if os.path.exists(CACHE_FILE):

        with open(CACHE_FILE, 'rb') as cache:
            watchmode_movie_dict = pickle.load(cache)
    else:
        watchmode_movie_dict = defaultdict(list)   

        with open(WATCHMODE_MAP_PATH,newline='\n', encoding='utf-8') as csvfile:

            for record in csv.DictReader(csvfile):
                for k,v in record.items():
                    if type(k) is str:
                        k = k.strip()
                    watchmode_movie_dict[k].append(v)
        
        with open(CACHE_FILE, 'wb') as cache:
            pickle.dump(watchmode_movie_dict, cache)
    
    ret = {}
    
    for k,v in watchmode_movie_dict.items():
        if k is None:
            k = 'None'
        new_k = k.lower().strip().replace(' ','_')
        ret[new_k] = v
        print(new_k)
    print(ret.get('none',None))
    return ret

# exit(101)
watchmode_csvdict = __main()

# imdb_ids,tmdb_ids = op.itemgetter('IMDB ID','TMDB ID')(watchmode_movie_dict)

# print(watchmode_movie_dict.keys())

# print(
#     min(filter(lambda x: x is not None and x != '' and x != 'null',imdb_ids),key=len),max(imdb_ids,key=len),
#     )
# print(
#     min(tmdb_ids,key=len),max(tmdb_ids,key=len),
#     )
# for imdb_id,tmdb_id in zip(imdb_ids,tmdb_ids):
#     pass