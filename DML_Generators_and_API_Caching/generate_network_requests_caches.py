import requests
import csv
import json

import os
import time
import pickle

import functools
import datetime
from line_profiler import LineProfiler

from tqdm import tqdm

csv_file1 = 'books_final_antoine.csv'
csv_file2 = 'authors_final_antoine.csv'
# csv_file1 = 'books_antoine.csv'
# csv_file2 = 'authors_antoine.csv'
json_file1 = 'reviewers_final_antoine.json'
json_file2 = 'reviews_final_antoine.json'
json_file3 = 'authoruids2.json'


#data4_cache_file = 'data4_final_cache.pkl'
data4_cache_file = 'data4_cache.pkl'

def profile(*,custom_mname:str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            prof = LineProfiler()
            try:
                return prof(func)(*args, **kwargs)
            finally:

                loggedtime = datetime.datetime.now()\
                                .strftime("%Y-%m-%d %H-%M-%S")

                #   current_dir = os.path.dirname(os.path.abspath(__file__))
                #  FILE_NAME = os.path.join(current_dir, 'prefs', 'recent_directories.pkl')

                with open(
                        rf"[{loggedtime}]{custom_mname}.log",
                        'w+'
                ) as logfile:

                    prof.print_stats(stream=logfile)

        return wrapper
    return decorator


#TODO @profile(custom_mname="dml_generator")
def main():
    print("STARTING!")
    
    data1 = {} # raw books
    row_index = 0
    with open(csv_file1, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            if row["isbn13"].endswith(".0"):
                row["isbn13"] = row["isbn13"][:-2]
            data1[row_index] = row
            row_index += 1
    # print(json.dumps(data1, indent=4))
    print("data1 finished")
    data2 = {} # books with wanted columns
    for key, row in data1.items():
        if all(field in row for field in ["url", "author", "characters", "places", "isbn13", "series"]) and row["isbn13"]:
            url = row["url"]
            last_slash_index = url.rfind("/")
            gid = url[last_slash_index + 1:]
            data2[key] = {
                "gid": gid,
                "author": row["author"],
                "characters": row["characters"],
                "places": row["places"],
                "isbn13": row["isbn13"],
                "series": row["series"]
            }
        #! elif 'isbn13'in row['description'].lower() or 'isbn 13'in row['description'].lower() or 'isbn_13'in row['description'].lower():
            
        #!     data2[key] = None
    print(len(data1),len(data2))
    
    # print(json.dumps(data2, indent=4))
    print("data2 finished")
    data3 = {} # raw authors
    row_index = 0
    with open(csv_file2, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            data3[row_index] = row
            row_index += 1
    # print(json.dumps(data3, indent=4))
    print("data3 finished")
    
    if False and os.path.exists(data4_cache_file):
        # Load data4 from cache file
        with open(data4_cache_file, 'rb') as f:
            data4 = pickle.load(f)
        print("Data4 loaded from cache")
    else:
        outer_progress_bar = tqdm(total=len(data2), desc="Outer Loop")
        
        data4 = {} # wanted authors
        au_int = 1
        for key1, row1 in data2.items():
            author_name1 = row1.get("author")
            authors_list = author_name1.strip("[]").replace("'", "").split(", ")
            
            
            inner_progress_bar = tqdm(total=len(authors_list), desc="Inner Loop", leave=False)
            
            for author in authors_list:
                
                # inner2_progress_bar = tqdm(total=len(data3), desc="Inner #2 Loop", leave=False)
                
                for key2, row2 in data3.items():
                    author_name2 = row2.get("name")
                    if author.lower() == author_name2.lower():
                        url = data3[key2]["url"]
                        last_slash_index = url.rfind("/")
                        gid = url[last_slash_index + 1:]
                        data4[au_int] = {
                            "author_gid": gid,
                            "isbn13": data2[key1]["isbn13"],
                            "name": data3[key2]["name"],
                            "birthDate": data3[key2]["birthDate"],
                            "deathDate": data3[key2]["deathDate"],
                            "avgRating": data3[key2]["avgRating"],
                            "reviewsCount": data3[key2]["reviewsCount"],
                            "ratingsCount": data3[key2]["ratingsCount"],
                            "about": data3[key2]["about"]
                        }
                        au_int += 1
                    # inner2_progress_bar.update(1)
                    
                inner_progress_bar.update(1)
                # inner2_progress_bar.close()
                
            outer_progress_bar.update(1)
            inner_progress_bar.close()
            
        outer_progress_bar.close()
        # print(json.dumps(data4, indent=4))
        
        with open(data4_cache_file, 'wb') as f:
            pickle.dump(data4, f)
        print("Data4 generated and cached")
        
    print("RAW (Part1) data4 finished")
    
    data7 = {} # AUTHORS WITH GOODREADS ACC
    with open(json_file3, 'r') as json_file:
        data7 = json.load(json_file)
        filtered_data7 = [d for d in data7 if "user_gid_url" in d]

    for d in filtered_data7: # PARSE URL FOR IDS
        if "author_url" in d:
            d["author_url"] = d["author_url"].rsplit("/", 1)[-1]
        if "user_gid_url" in d:
            d["user_gid_url"] = d["user_gid_url"].rsplit("/", 1)[-1]
    # print(json.dumps(filtered_data7, indent=4))
    print("FilteredData7+Gids (Part2) data4 finished")
    for key88, value88 in data4.items(): # ADD THE IDS TO AUTHORS
        for auti in filtered_data7:
            if value88["author_gid"] == auti["author_url"]:
                value88["user_gid"] = auti["user_gid_url"]
            else:
                value88["user_gid"] = ""
    # print(json.dumps(data4, indent=4))
    print("data4 fully finished")


    data5 = {} # raw reviewers
    with open(json_file1, 'r') as json_file:
        data5 = json.load(json_file)
    # print(json.dumps(data5, indent=4))

    print("data5 finished")
    data6 = {} # raw reviews
    with open(json_file2, 'r') as json_file:
        data6 = json.load(json_file)

    # print(json.dumps(data6, indent=4))
    print("data6 finished")
    

    print("LOADING ALL FILES DONE") 

    # Function to fetch book data from Google Books API using ISBN
    def fetch_google_book_data(isbn):
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        response = requests.get(url)
        data = response.json()
        return data

    # Function to create a dictionary of book data from Google Books API response
    def create_book_dict(isbn):
        # Fetch book data from Google Books API using the provided ISBN
        book_data = fetch_google_book_data(isbn)
        # Initialize an empty dictionary to store book information
        book_dict = {}
        # Check if the 'items' key exists in the book data
        if 'items' in book_data:
            # Initialize a counter variable
            i = 0
            # Extract the list of items from the book data
            items = book_data['items']
            # Iterate over each item in the list of items
            for item in items:
                # Extract volume information from the item, if available
                volume_info = item.get('volumeInfo', {})
                # Add volume information to the book dictionary at index i
                book_dict[i] = volume_info
                # Extract additional information and add it to the book dictionary
                book_dict[i]["id"] = item.get('id', {})
                book_dict[i]["saleInfo"] = item.get('saleInfo', {})
                book_dict[i]["accessInfo"] = item.get('accessInfo', {})
                # Increment the counter variable for the next index
                i += 1
        # Return the dictionary containing book information
        return book_dict

    # Function to fetch book data from Open Library API using ISBN
    def fetch_ol_book_data(isbn):
        url = f"https://openlibrary.org/isbn/{isbn}.json"
        response = requests.get(url)
        try:
            data = response.json()
            return data
        except Exception as e:
            return None

    # Function to fetch subjects from Open Library Work API
    def fetch_ol_work_data(path):
        url = f"https://openlibrary.org/{path}.json"
        response = requests.get(url)
        data = response.json()
        try:
            return data["subjects"]
        except Exception as e:
            return None

    def handle_null(value): # NEEDED FOR NULL INSTEAD OF NONE OR ""
        return "NULL" if value is None or value == "" else value

    
    def delete_files_if_exist(*files):
        for file in files:
            if os.path.exists(file):
                os.remove(file)
    # INITIALIZATION FOR IDS, SETS, AND COUNTS
    count = 0
    genreID = 1
    subjectID = 1
    publisherID = 1
    bookID = 1
    thumbnailID = 0
    retailID = 0
    listID = 0

    bookgenreID = 0
    booksubjectID = 0
    bookpublisherID = 0

    characterID = 1
    bookcharacterID = 0
    placeID = 1
    bookplaceID = 0
    seriesID = 1
    bookseriesID = 0

    personID = 1
    authorID = 1
    bookauthorID = 1

    reviewerID = 1


    reviewer_flag = 0
    author_flag = 0

    characters_cache = set()
    genre_cache = set()
    subject_cache = set()
    publisher_cache = set()
    place_cache = set()
    series_cache = set()
    person_cache = set()

    reviewer_cache = set()
    book_cache = set()

    
    # Delete text files from idk functions
    # delete_files_if_exist('person.txt', 'author.txt','bookauthor.txt', 
    #                       'reviewer.txt','bookreview.txt')
    
    # # Delete existing files before opening them in append mode
    # delete_files_if_exist('genre.txt', 'subject.txt', 'publisher.txt', 'book.txt', 'thumbnail.txt', 
    #                     'retail.txt', 'bookgenre.txt', 'booksubject.txt', 'bookpublisher.txt', 
    #                     'character.txt', 'bookcharacter.txt', 'place.txt', 'bookplace.txt', 
    #                     'series.txt', 'bookseries.txt', 'list.txt')
    # Must do this to avoid SyntaxError: too many statically nested blocks error on most hardware with a lot of Open()
    person_file_content = ""
    author_file_content = ""
    bookauthor_file_content = ""
    reviewer_file_content = ""
    bookreview_file_content = ""
    
    spec_dict_request_cache = dict()
    
    with open(r"final_spec_dict_request_cache.json", 'w') as file:
        try:    
            N = len(data2)
            # value_ix = 0
            request_caching_progressbar = tqdm(total=N, desc="Data2 3x Requests Caching")
            
            for key, value in data2.items():
            # Open the files in append mode
                # value_ix += 1
                
                # print(f"value6 in data6 is : {(value_ix / N)*100} % done",
                #     end=46*"\b" + "\r",flush=True)
                # Iterate over each ISBN in the file
                count += 1
                isbn13 = value["isbn13"]
                
                #! Added try accept to avoid request connnection error with google books API
                
                try:
                    # Create a dictionary of book data from Google Books API
                    book_dict = create_book_dict(isbn13)
                except Exception as badRequestSkipBecauseGoogleBooks:
                    print(f"badRequestSkipBecauseGoogleBooks: {badRequestSkipBecauseGoogleBooks}",end="\n *** \n")
                    count -= 1
                    continue
                
                
                
                spec_dict = {}
                
                try:
                    # Iterate over each book entry in the dictionary
                    for book_key in book_dict:
                        # Populate the spec_dict with relevant book information
                        spec_dict["volume_id"] = book_dict[book_key]["id"]
                        spec_dict["title"] = book_dict[book_key]["title"]
                        spec_dict["subtitle"] = book_dict[book_key].get("subtitle", None)
                        spec_dict["authors"] = book_dict[book_key].get("authors", None)
                        spec_dict["publisher"] = book_dict[book_key].get("publisher", None)
                        spec_dict["publishedDate"] = book_dict[book_key].get("publishedDate", None)
                        spec_dict["description"] = book_dict[book_key].get("description", None)
                        try:
                            spec_dict["isbn_10"] = book_dict[book_key]["industryIdentifiers"][1]["identifier"]
                        except (IndexError, KeyError):
                            spec_dict["isbn_10"] = None
                        spec_dict["isbn_13"] = isbn13 #book_dict[book_key]["industryIdentifiers"][0]["identifier"]
                        spec_dict["viewable_text"] = book_dict[book_key]["readingModes"].get("text", None)
                        spec_dict["viewable_image"] = book_dict[book_key]["readingModes"].get("image", None)
                        spec_dict["pageCount"] = book_dict[book_key].get("pageCount", None)
                        spec_dict["genre"] = book_dict[book_key].get("categories", None)
                        spec_dict["averageRating"] = book_dict[book_key].get("averageRating", None)
                        spec_dict["ratingsCount"] = book_dict[book_key].get("ratingsCount", None)
                        spec_dict["maturityRating"] = book_dict[book_key].get("maturityRating", None)
                        spec_dict["content_version"] = book_dict[book_key].get("contentVersion", None)
                        spec_dict["thumbnails"] = book_dict[book_key].get("imageLinks", None)
                        spec_dict["language"] = book_dict[book_key].get("language", None)
                        spec_dict["previewLink"] = book_dict[book_key].get("previewLink", None)
                        spec_dict["infoLink"] = book_dict[book_key].get("infoLink", None)
                        spec_dict["canonicalVolumeLink"] = book_dict[book_key].get("canonicalVolumeLink", None)
                        spec_dict["listPrice"] = book_dict[book_key]["saleInfo"].get("listPrice", None)
                        spec_dict["retailPrice"] = book_dict[book_key]["saleInfo"].get("retailPrice", None)
                        spec_dict["epub_available"] = book_dict[book_key]["accessInfo"]["epub"].get("isAvailable", None)
                        spec_dict["pdf_available"] = book_dict[book_key]["accessInfo"]["pdf"].get("isAvailable", None)
                except:
                    continue
                #! Added try accept to avoid request connnection error with open library API
                try:
                    # Fetch book data from Open Library API
                    ol_dict = fetch_ol_book_data(isbn13)
                except Exception as badRequestSkipBecauseOpenLibraryBooks:
                    print(f"badRequestSkipBecauseOpenLibraryBooks: {badRequestSkipBecauseOpenLibraryBooks}",end="\n *** \n")
                    count -= 1
                    continue
                
                if ol_dict is not None and "key" in ol_dict:
                    spec_dict["ol_book_id"] = ol_dict["key"]
                    try:
                        spec_dict["ol_work_id"] = ol_dict["works"][0]["key"]
                        spec_dict["subjects"] = fetch_ol_work_data(spec_dict["ol_work_id"])
                    except Exception as e:
                        spec_dict["ol_work_id"] = None
                        spec_dict["subjects"] = None


                spec_dict_request_cache.setdefault(isbn13,spec_dict) #!!!!!!!!!!!!!!!!!
                request_caching_progressbar.update(1)
        except:
            request_caching_progressbar.close()
            json.dump(spec_dict_request_cache, file)
        else:
            request_caching_progressbar.close()
            json.dump(spec_dict_request_cache, file)
    # # loop isbn
    # with open('genre.txt', 'a', encoding='utf-8') as genre_file, \
    #     open('subject.txt', 'a', encoding='utf-8') as subject_file, \
    #     open('publisher.txt', 'a', encoding='utf-8') as publisher_file, \
    #     open('book.txt', 'a', encoding='utf-8') as book_file, \
    #     open('thumbnail.txt', 'a', encoding='utf-8') as thumbnail_file, \
    #     open('retail.txt', 'a', encoding='utf-8') as retail_file, \
    #     open('bookgenre.txt', 'a', encoding='utf-8') as bookgenre_file, \
    #     open('booksubject.txt', 'a', encoding='utf-8') as booksubject_file, \
    #     open('bookpublisher.txt', 'a', encoding='utf-8') as bookpublisher_file, \
    #     open('character.txt', 'a', encoding='utf-8') as character_file, \
    #     open('bookcharacter.txt', 'a', encoding='utf-8') as bookcharacter_file, \
    #     open('place.txt', 'a', encoding='utf-8') as place_file, \
    #     open('bookplace.txt', 'a', encoding='utf-8') as bookplace_file, \
    #     open('series.txt', 'a', encoding='utf-8') as series_file, \
    #     open('bookseries.txt', 'a', encoding='utf-8') as bookseries_file, \
    #     open('list.txt', 'a', encoding='utf-8') as list_file:
    #     # open('person.txt', 'a', encoding='utf-8') as person_file,\
    #     # open('author.txt', 'a', encoding='utf-8') as author_file, \
    #     # open('bookauthor.txt', 'a', encoding='utf-8') as bookauthor_file, \
    #     # open('reviewer.txt', 'a', encoding='utf-8') as reviewer_file, \
    #     # open('bookreview.txt', 'a', encoding='utf-8') as bookreview_file:
        
    #     N = len(data2)
    #     value_ix = 0
    #     for key, value in data2.items():
    #         # Open the files in append mode
    #             value_ix += 1
    #             print(f"value6 in data6 is : {value_ix / N} % done",
    #                 end=46*"\b" + "\r",flush=True)
    #             # Iterate over each ISBN in the file
    #             count += 1
    #             isbn13 = value["isbn13"]
                
    #             #! Added try accept to avoid request connnection error with google books API
                
    #             try:
    #                 # Create a dictionary of book data from Google Books API
    #                 book_dict = create_book_dict(isbn13)
    #             except Exception as badRequestSkipBecauseGoogleBooks:
    #                 print(f"badRequestSkipBecauseGoogleBooks: {badRequestSkipBecauseGoogleBooks}",end="\n *** \n")
    #                 count -= 1
    #                 continue
                
                
                
    #             spec_dict = {}
                
                
    #             # Iterate over each book entry in the dictionary
    #             for book_key in book_dict:
    #                 # Populate the spec_dict with relevant book information
    #                 spec_dict["volume_id"] = book_dict[book_key]["id"]
    #                 spec_dict["title"] = book_dict[book_key]["title"]
    #                 spec_dict["subtitle"] = book_dict[book_key].get("subtitle", None)
    #                 spec_dict["authors"] = book_dict[book_key].get("authors", None)
    #                 spec_dict["publisher"] = book_dict[book_key].get("publisher", None)
    #                 spec_dict["publishedDate"] = book_dict[book_key].get("publishedDate", None)
    #                 spec_dict["description"] = book_dict[book_key].get("description", None)
    #                 try:
    #                     spec_dict["isbn_10"] = book_dict[book_key]["industryIdentifiers"][1]["identifier"]
    #                 except (IndexError, KeyError):
    #                     spec_dict["isbn_10"] = None
    #                 spec_dict["isbn_13"] = isbn13 #book_dict[book_key]["industryIdentifiers"][0]["identifier"]
    #                 spec_dict["viewable_text"] = book_dict[book_key]["readingModes"].get("text", None)
    #                 spec_dict["viewable_image"] = book_dict[book_key]["readingModes"].get("image", None)
    #                 spec_dict["pageCount"] = book_dict[book_key].get("pageCount", None)
    #                 spec_dict["genre"] = book_dict[book_key].get("categories", None)
    #                 spec_dict["averageRating"] = book_dict[book_key].get("averageRating", None)
    #                 spec_dict["ratingsCount"] = book_dict[book_key].get("ratingsCount", None)
    #                 spec_dict["maturityRating"] = book_dict[book_key].get("maturityRating", None)
    #                 spec_dict["content_version"] = book_dict[book_key].get("contentVersion", None)
    #                 spec_dict["thumbnails"] = book_dict[book_key].get("imageLinks", None)
    #                 spec_dict["language"] = book_dict[book_key].get("language", None)
    #                 spec_dict["previewLink"] = book_dict[book_key].get("previewLink", None)
    #                 spec_dict["infoLink"] = book_dict[book_key].get("infoLink", None)
    #                 spec_dict["canonicalVolumeLink"] = book_dict[book_key].get("canonicalVolumeLink", None)
    #                 spec_dict["listPrice"] = book_dict[book_key]["saleInfo"].get("listPrice", None)
    #                 spec_dict["retailPrice"] = book_dict[book_key]["saleInfo"].get("retailPrice", None)
    #                 spec_dict["epub_available"] = book_dict[book_key]["accessInfo"]["epub"].get("isAvailable", None)
    #                 spec_dict["pdf_available"] = book_dict[book_key]["accessInfo"]["pdf"].get("isAvailable", None)

    #             #! Added try accept to avoid request connnection error with open library API
    #             try:
    #                 # Fetch book data from Open Library API
    #                 ol_dict = fetch_ol_book_data(isbn13)
    #             except Exception as badRequestSkipBecauseOpenLibraryBooks:
    #                 print(f"badRequestSkipBecauseOpenLibraryBooks: {badRequestSkipBecauseOpenLibraryBooks}",end="\n *** \n")
    #                 count -= 1
    #                 continue
                
    #             if ol_dict is not None:
    #                 spec_dict["ol_book_id"] = ol_dict["key"]
    #                 try:
    #                     spec_dict["ol_work_id"] = ol_dict["works"][0]["key"]
    #                     spec_dict["subjects"] = fetch_ol_work_data(spec_dict["ol_work_id"])
    #                 except Exception as e:
    #                     spec_dict["ol_work_id"] = None
    #                     spec_dict["subjects"] = None


    #             spec_dict_request_cache.setdefault(isbn13,spec_dict) #!!!!!!!!!!!!!!!!!
    #             continue
                
    #             # Write genre data to a file
    #             try:
    #                 for genre in spec_dict["genre"]:
    #                     if genre is not None:
    #                         genreHasAlreadyBeenSeen: bool = any(genre in set_item for set_item in genre_cache)
    #                         if not genreHasAlreadyBeenSeen:
    #                             genre_file.write(
    #                                 f"INSERT IGNORE INTO genre (genre_id, genre_name) VALUES ({genreID}, '{genre}');\n")
    #                             bookgenre_file.write(
    #                                 f"INSERT IGNORE INTO bookgenre (bookgenre_id, genre_id, book_id) VALUES ({(bookgenreID := bookgenreID + 1)}, {genreID}, {bookID});\n")
    #                             genre_cache.add(frozenset((genreID, genre)))
    #                             genreID = genreID + 1
    #                         elif genreHasAlreadyBeenSeen:
    #                             genre_set = next(
    #                                 set_item for set_item in genre_cache if genre in set_item
    #                             )
    #                             existing_genreID = next(iter(genre_set))
    #                             if not isinstance(existing_genreID, int):
    #                                 existing_genreID = next(iter(genre_set - {existing_genreID}))
    #                             bookgenre_file.write(
    #                                 f"INSERT IGNORE INTO bookgenre (bookgenre_id, genre_id, book_id) VALUES ({(bookgenreID := bookgenreID + 1)}, {existing_genreID}, {bookID});\n")

    #             except Exception as e:
    #                 # Handle exceptions if any
    #                 pass

    #             # Write subject data to a file
    #             try:
    #                 for subject in spec_dict["subjects"]:
    #                     if subject is not None:
    #                         subjectHasAlreadyBeenSeen: bool = any(subject in set_item for set_item in subject_cache)
    #                         if not subjectHasAlreadyBeenSeen:
    #                             subject_file.write(
    #                                 f"INSERT IGNORE INTO subject (subject_id, subject_name) VALUES ({subjectID}, '{subject}');\n")
    #                             booksubject_file.write(
    #                                 f"INSERT IGNORE INTO booksubject (booksubject_id, subject_id, book_id) VALUES ({(booksubjectID := booksubjectID + 1)}, {subjectID}, {bookID});\n")
    #                             subject_cache.add(frozenset((subjectID, subject)))
    #                             subjectID = subjectID + 1
    #                         elif subjectHasAlreadyBeenSeen:
    #                             subject_set = next(
    #                                 set_item for set_item in subject_cache if subject in set_item
    #                             )
    #                             existing_subjectID = next(iter(subject_set))
    #                             if not isinstance(existing_subjectID, int):
    #                                 existing_subjectID = next(iter(subject_set - {existing_subjectID}))
    #                             booksubject_file.write(
    #                                 f"INSERT IGNORE INTO booksubject (booksubject_id, subject_id, book_id) VALUES ({(booksubjectID := booksubjectID + 1)}, {existing_subjectID}, {bookID});\n")
    #             except Exception as e:
    #                 pass

    #             # Write publisher data to a file
    #             try:
    #                 if spec_dict['publisher'] is not None:
    #                     publisherHasAlreadyBeenSeen: bool = any(spec_dict['publisher'] in set_item for set_item in publisher_cache)
    #                     if not publisherHasAlreadyBeenSeen:
    #                         publisher_file.write(
    #                             f"INSERT IGNORE INTO publisher (publisher_id, publisher_name) VALUES ({publisherID}, '{spec_dict['publisher']}');\n")
    #                         bookpublisher_file.write(
    #                             f"INSERT IGNORE INTO bookpublisher (bookpublisher_id, publisher_id, book_id) VALUES ({(bookpublisherID := bookpublisherID + 1)}, {publisherID}, {bookID});\n")
    #                         publisher_cache.add(frozenset((publisherID, spec_dict['publisher'])))
    #                         publisherID = publisherID + 1
    #                     elif publisherHasAlreadyBeenSeen:
    #                         publisher_set = next(
    #                             set_item for set_item in publisher_cache if spec_dict['publisher'] in set_item
    #                         )
    #                         existing_publisherID = next(iter(publisher_set))
    #                         if not isinstance(existing_publisherID, int):
    #                             existing_publisherID = next(iter(publisher_set - {existing_publisherID}))
    #                         bookpublisher_file.write(
    #                             f"INSERT IGNORE INTO bookpublisher (bookpublisher_id, publisher_id, book_id) VALUES ({(bookpublisherID := bookpublisherID + 1)}, {existing_publisherID}, {bookID});\n")
    #             except Exception as e:
    #                 pass

    #             # Write book data to a file
    #             try:
    #                 before_null = f"INSERT IGNORE INTO book (book_id, volume_id, ol_book_id, ol_work_id, title, subtitle, publishedDate, description, isbn_10, isbn_13, pageCount, content_version, viewable_image, viewable_text, averageRating, ratingsCount, maturityRating, language, previewLink, infoLink, pdf_available, epub_available, book_gid) VALUES ({bookID}, '{spec_dict['volume_id']}', '{spec_dict['ol_book_id']}', '{handle_null(spec_dict.get('ol_work_id', ''))}', '{spec_dict['title']}', '{handle_null(spec_dict.get('subtitle', ''))}', '{handle_null(spec_dict.get('publishedDate', ''))}', '{handle_null(spec_dict.get('description', 'NULL'))}', '{handle_null(spec_dict.get('isbn_10', 'NULL'))}', '{spec_dict['isbn_13']}', {handle_null(spec_dict.get('pageCount', ''))}, '{handle_null(spec_dict.get('content_version', ''))}', {handle_null(spec_dict.get('viewable_image', ''))}, {handle_null(spec_dict.get('viewable_text', ''))}, {handle_null(spec_dict.get('averageRating', ''))}, {handle_null(spec_dict.get('ratingsCount', ''))}, '{handle_null(spec_dict.get('maturityRating', ''))}', '{handle_null(spec_dict.get('language', ''))}', '{handle_null(spec_dict.get('previewLink', ''))}', '{handle_null(spec_dict.get('infoLink', ''))}', {handle_null(spec_dict.get('pdf_available', ''))}, {handle_null(spec_dict.get('epub_available', ''))}, '{handle_null(spec_dict.get('gid', ''))}');\n"
    #                 # Remove '...' around the NULLs
    #                 modified_before_null = before_null
    #                 null_index = modified_before_null.find("'NULL'")
    #                 while null_index != -1:
    #                     modified_before_null = modified_before_null[:null_index] + modified_before_null[
    #                                                                             null_index + 1:null_index + 5] + modified_before_null[
    #                                                                                                                 null_index + 6:]
    #                     null_index = modified_before_null.find("'NULL'", null_index)

    #                 book_file.write(modified_before_null)
    #                 book_cache.add(frozenset((bookID, value["gid"])))
    #             except Exception as e:
    #                 pass

    #             # Write thumbnail data to a file
    #             try:
    #                 for thumbnail in spec_dict["thumbnails"]:
    #                     if spec_dict['thumbnails'] is not None:
    #                         thumbnail_file.write(
    #                             f"INSERT IGNORE INTO thumbnail (thumbnail_id, book_id, link) VALUES ({(thumbnailID := thumbnailID + 1)}, {bookID}, '{spec_dict['thumbnails'][thumbnail]}');\n")
    #             except Exception as e:
    #                 pass

    #             # Write retail data to a file
    #             try:
    #                 if spec_dict['retailPrice'] is not None:
    #                     retail_file.write(
    #                         f"INSERT IGNORE INTO retailPrice (retailPrice_id, book_id, currencyCode, amount) VALUES ({(retailID := retailID + 1)}, {bookID}, '{spec_dict['retailPrice']['currencyCode']}', {spec_dict['retailPrice']['amount']});\n")
    #             except Exception as e:
    #                 pass

    #             # Write list data to a file
    #             try:
    #                 if spec_dict['listPrice'] is not None:
    #                     list_file.write(
    #                             f"INSERT IGNORE INTO listPrice (listPrice_id, book_id, currencyCode, amount) VALUES ({(listID := listID + 1)}, {bookID}, '{spec_dict['listPrice']['currencyCode']}', {spec_dict['listPrice']['amount']});\n")
    #             except Exception as e:
    #                 pass

    #             # Write character data to a file
    #             characters = value.get("characters")
    #             if characters != "":
    #                 characters_list = characters.strip("[]").replace("'", "").split(", ")
    #                 for character in characters_list:
    #                     chHasAlreadyBeenSeen: bool = any(character in set_item for set_item in characters_cache)
    #                     if not chHasAlreadyBeenSeen:
    #                         character_file.write(
    #                                 f"INSERT IGNORE INTO characterr (character_id, character_name) VALUES ({characterID}, '{character}');\n")
    #                         bookcharacter_file.write(
    #                                 f"INSERT IGNORE INTO bookcharacter (bookcharacter_id, character_id, book_id) VALUES ({(bookcharacterID := bookcharacterID + 1)}, {characterID}, {bookID});\n")
    #                         characters_cache.add(frozenset((characterID, character)))
    #                         characterID = characterID + 1
    #                     elif chHasAlreadyBeenSeen:
    #                         character_set = next(
    #                             set_item for set_item in characters_cache if character in set_item
    #                         )
    #                         existing_characterID = next(iter(character_set))
    #                         if not isinstance(existing_characterID, int):
    #                             existing_characterID = next(iter(character_set - {existing_characterID}))
    #                         bookcharacter_file.write(
    #                             f"INSERT IGNORE INTO bookcharacter (bookcharacter_id, character_id, book_id) VALUES ({(bookcharacterID := bookcharacterID + 1)}, {existing_characterID}, {bookID});\n")

    #             # Write place data to a file
    #             places = value.get("places")
    #             if places != "":
    #                 places_list = places.strip("[]").replace("'", "").split(", ")
    #                 for place in places_list:
    #                     placeHasAlreadyBeenSeen: bool = any(place in set_item for set_item in place_cache)
    #                     if not placeHasAlreadyBeenSeen:
    #                         place_file.write(
    #                             f"INSERT IGNORE INTO place (place_id, place_name) VALUES ({placeID}, '{place}');\n")
    #                         bookplace_file.write(
    #                             f"INSERT IGNORE INTO bookplace (bookplace_id, place_id, book_id) VALUES ({(bookplaceID := bookplaceID + 1)}, {placeID}, {bookID});\n")
    #                         place_cache.add(frozenset((placeID, place)))
    #                         placeID = placeID + 1
    #                     elif placeHasAlreadyBeenSeen:
    #                         place_set = next(
    #                             set_item for set_item in place_cache if place in set_item
    #                         )
    #                         existing_placeID = next(iter(place_set))
    #                         if not isinstance(existing_placeID, int):
    #                             existing_placeID = next(iter(place_set - {existing_placeID}))
    #                         bookplace_file.write(
    #                             f"INSERT IGNORE INTO bookplace (bookplace_id, place_id, book_id) VALUES ({(bookplaceID := bookplaceID + 1)}, {existing_placeID}, {bookID});\n")

    #             # Write series data to a file
    #             series = value.get("series")
    #             if series != "":
    #                 series_list = series.strip("[]").replace("'", "").split(", ")
    #                 for seriess in series_list:
    #                     try:
    #                         seriesHasAlreadyBeenSeen: bool = any(seriess in set_item for set_item in series_cache)
    #                         if not seriesHasAlreadyBeenSeen:
    #                             series_file.write(
    #                                 f"INSERT IGNORE INTO series (series_id, series_name) VALUES ({seriesID}, '{seriess}');\n")
    #                             bookseries_file.write(
    #                                 f"INSERT IGNORE INTO bookseries (bookseries_id, series_id, book_id) VALUES ({(bookseriesID := bookseriesID + 1)}, {seriesID}, {bookID});\n")
    #                             series_cache.add(frozenset((seriesID, seriess)))
    #                             seriesID = seriesID + 1
    #                         elif seriesHasAlreadyBeenSeen:
    #                             series_set = next(
    #                                 set_item for set_item in series_cache if seriess in set_item
    #                             )
    #                             existing_seriesID = next(iter(series_set))
    #                             if not isinstance(existing_seriesID, int):
    #                                 existing_seriesID = next(iter(series_set - {existing_seriesID}))
    #                             bookseries_file.write(
    #                                 f"INSERT IGNORE INTO bookseries (bookseries_id, series_id, book_id) VALUES ({(bookseriesID := bookseriesID + 1)}, {existing_seriesID}, {bookID});\n")
    #                     except Exception as e:
    #                         pass

    #             # Write person and author data to a file
    #             for key4, value4 in data4.items():
    #                 if value4["isbn13"] == isbn13:
    #                     personHasAlreadyBeenSeen: bool = any(value4['user_gid']+"_NAH" in set_item for set_item in person_cache)
    #                     if not personHasAlreadyBeenSeen:
    #                         #! idk1
    #                         person_file_content += f"INSERT IGNORE INTO person (person_id, person_name, user_gid) VALUES ({personID}, '{value4['name']}', '{value4['user_gid']}');\n"

    #                         before_null = f"INSERT IGNORE INTO author (author_id, person_id, birthDate, deathDate, avgRating, reviewsCount, ratingsCount, about, author_gid) VALUES ({authorID}, {personID}, '{handle_null(value4.get('birthDate', None))}', '{handle_null(value4.get('deathDate', None))}', {handle_null(value4.get('avgRating', None))}, {handle_null(value4.get('reviewsCount', None))}, {handle_null(value4.get('ratingsCount', None))}, '{handle_null(value4.get('about', None))}', '{handle_null(value4.get('author_gid', None))}');\n"
    #                         # Remove '...' around the NULLs
    #                         modified_before_null = before_null
    #                         null_index = modified_before_null.find("'NULL'")
    #                         while null_index != -1:
    #                             modified_before_null = modified_before_null[:null_index] + modified_before_null[
    #                                                                                     null_index + 1:null_index + 5] + modified_before_null[
    #                                                                                                                         null_index + 6:]
    #                             null_index = modified_before_null.find("'NULL'", null_index)
    #                         #! idk2
    #                         author_file_content +=  str(modified_before_null)
    #                         #! idk3
    #                         bookauthor_file_content += f"INSERT IGNORE INTO bookauthor (bookauthor_id, author_id, book_id) VALUES ({bookauthorID}, {authorID}, {bookID});\n"
                            
    #                         if value4['user_gid'] != "":
    #                             person_cache.add(frozenset((personID, value4['user_gid']+"_NAH")))
    #                         authorID = authorID + 1
    #                         personID = personID + 1
    #                         bookauthorID = bookauthorID + 1
    #                     elif personHasAlreadyBeenSeen:
    #                         person_set = next(
    #                             set_item for set_item in person_cache if value4['user_gid']+"_NAH" in set_item
    #                         )
    #                         existing_personID = next(iter(person_set))
    #                         if not isinstance(existing_personID, int):
    #                             existing_personID = next(iter(person_set - {existing_personID}))
                            
    #                         before_null = f"INSERT IGNORE INTO author (author_id, person_id, birthDate, deathDate, avgRating, reviewsCount, ratingsCount, about, author_gid) VALUES ({authorID}, {existing_personID}, '{handle_null(value4.get('birthDate', None))}', '{handle_null(value4.get('deathDate', None))}', {handle_null(value4.get('avgRating', None))}, {handle_null(value4.get('reviewsCount', None))}, {handle_null(value4.get('ratingsCount', None))}, '{handle_null(value4.get('about', None))}', '{handle_null(value4.get('author_gid', None))}');\n"
    #                         # Remove '...' around the NULLs
    #                         modified_before_null = before_null
    #                         null_index = modified_before_null.find("'NULL'")
    #                         while null_index != -1:
    #                             modified_before_null = modified_before_null[:null_index] + modified_before_null[
    #                                                                                     null_index + 1:null_index + 5] + modified_before_null[
    #                                                                                                                         null_index + 6:]
    #                             null_index = modified_before_null.find("'NULL'", null_index)
    #                         #! idk2
    #                         author_file_content += str(modified_before_null)
    #                         #! idk3
    #                         bookauthor_file_content += f"INSERT IGNORE INTO bookauthor (bookauthor_id, author_id, book_id) VALUES ({bookauthorID}, {authorID}, {bookID});\n"
    #                         authorID = authorID + 1
    #                         bookauthorID = bookauthorID + 1

    #             # Write person and reviewer data to a file
    #             end_now = 0 # TEMP CUZ TOO MUCH
    #             if reviewer_flag == 0:
    #                 for value5 in data5:
    #                     personHasAlreadyBeenSeen: bool = any(value5['reviewer_gid']+"_NAH" in set_item for set_item in person_cache)
    #                     if not personHasAlreadyBeenSeen:
    #                         #! idk1
    #                         person_file_content += f"INSERT IGNORE INTO person (person_id, person_name, user_gid) VALUES ({personID}, '{value5['name']}', '{value5['reviewer_gid']}');\n"

    #                         before_null = f"INSERT IGNORE INTO reviewer (reviewer_id, person_id, followersCount, isAuthor) VALUES ({reviewerID}, {personID}, {handle_null(value5.get('followersCount', None))}, {handle_null(value5.get('isAuthor', None))});\n"
    #                         # Remove '...' around the NULLs
    #                         modified_before_null = before_null
    #                         null_index = modified_before_null.find("'NULL'")
    #                         while null_index != -1:
    #                             modified_before_null = modified_before_null[:null_index] + modified_before_null[
    #                                                                                     null_index + 1:null_index + 5] + modified_before_null[
    #                                                                                                                         null_index + 6:]
    #                             null_index = modified_before_null.find("'NULL'", null_index)
    #                         #! idk4
    #                         reviewer_file_content += str(modified_before_null)
                            
    #                         reviewer_cache.add(frozenset((reviewerID, value5['reviewer_gid']+"_no")))
    #                         person_cache.add(frozenset((personID, value5['reviewer_gid']+"_NAH")))
    #                         reviewerID = reviewerID + 1
    #                         personID = personID + 1
    #                     elif personHasAlreadyBeenSeen:
    #                         person_set = next(
    #                             set_item for set_item in person_cache if value5['reviewer_gid']+"_NAH" in set_item
    #                         )
    #                         existing_personID = next(iter(person_set))
    #                         if not isinstance(existing_personID, int):
    #                             existing_personID = next(iter(person_set - {existing_personID}))
    #                         before_null = f"INSERT IGNORE INTO reviewer (reviewer_id, person_id, followersCount, isAuthor) VALUES ({reviewerID}, {existing_personID}, {handle_null(value5.get('followersCount', None))}, {handle_null(value5.get('isAuthor', None))});\n"
    #                         # Remove '...' around the NULLs
    #                         modified_before_null = before_null
    #                         null_index = modified_before_null.find("'NULL'")
    #                         while null_index != -1:
    #                             modified_before_null = modified_before_null[:null_index] + modified_before_null[
    #                                                                                     null_index + 1:null_index + 5] + modified_before_null[
    #                                                                                                                         null_index + 6:]
    #                             null_index = modified_before_null.find("'NULL'", null_index)
    #                         #! idk4
    #                         reviewer_file_content += str(modified_before_null)
    #                         reviewer_cache.add(frozenset((reviewerID, value5['reviewer_gid']+"_no")))
    #                         reviewerID = reviewerID + 1


    #                     end_now = end_now + 1
    #                     if end_now == 10000000: #! LIMIT OF REVIEWERS
    #                         break
    #                 reviewer_flag = 1
    #                 print("REVIEWER DONE")


    #             print(bookID)
    #             bookID = bookID + 1

    #             # Break the loop after processing a certain number of ISBNs
    #             if count > 10000: #! LIMIT OF BOOKS
    #                 print('Almost Done!')
    #                 break
        


    #     print("NOW DOING REVIEWS")
    #     # Write review data to a file
    #     bookreviewID = 1
    #     for value6_ix, value6 in enumerate(data6):
    #         #! print(f"value6 in data6 is : {value6_ix / len(data6)} % done",
    #         #!       end=46*"\b" + "\r",flush=True)
    #         print(f"value6 in data6 is : {value6_ix / len(data6)} % done",
    #                 end=46*"\b" + "\r",flush=True)
    #         reviewerHasAlreadyBeenSeen: bool = any(value6["reviewer_gid"]+"_no" in set_item for set_item in reviewer_cache)
    #         bookHasAlreadyBeenSeen: bool = any(value6["book_gid"] in set_item for set_item in book_cache)
            
            
    #         if reviewerHasAlreadyBeenSeen and bookHasAlreadyBeenSeen:
                
    #             reviewer_set = next(
    #                 set_item for set_item in reviewer_cache if value6["reviewer_gid"]+"_no" in set_item
    #             )
    #             existing_reviewerID = next(iter(reviewer_set))
    #             try:
    #                 test_int = int(existing_reviewerID)
    #             except Exception as e:
    #                 #print(e)
    #                 existing_reviewerID = next(iter(reviewer_set - {existing_reviewerID}))


    #             book_set = next(
    #                 set_item for set_item in book_cache if value6["book_gid"] in set_item
    #             )
    #             existing_bookID = next(iter(book_set))
    #             try:
    #                 test_int = int(existing_bookID)
    #             except Exception as e:
    #                 #print(e)
    #                 existing_bookID = next(iter(book_set - {existing_bookID}))

    #             #! idk5
    #             bookreview_file_content += f"INSERT IGNORE INTO bookreview (bookreview_id, reviewer_id, book_id, rev, created, updated, likeCount, rating) VALUES ({bookreviewID}, {existing_reviewerID}, {existing_bookID}, '{value6['text']}', '{value6['createdAt']}', '{value6['updatedAt']}', {value6['likeCount']}, {value6['rating']});\n"
    #             bookreviewID = bookreviewID + 1
    #             # print("YAYEEE")
    #     print('\n\n\rDone!')
    
    print("Writing the 5 remaining cached tables to their .txt")
    

    # with open('person.txt', 'a', encoding='utf-8') as person_file,\
    #     open('author.txt', 'a', encoding='utf-8') as author_file, \
    #     open('bookauthor.txt', 'a', encoding='utf-8') as bookauthor_file, \
    #     open('reviewer.txt', 'a', encoding='utf-8') as reviewer_file, \
    #     open('bookreview.txt', 'a', encoding='utf-8') as bookreview_file:
        
    #     person_file.write(person_file_content)
    #     author_file.write(author_file_content)
    #     bookauthor_file.write(bookauthor_file_content)
    #     reviewer_file.write(reviewer_file_content)
    #     bookreview_file.write(bookreview_file_content)
    print("ACTUALLY DONE NOW")
if __name__ == '__main__':
    
    #assert os.getcwd().split(os.sep)[-1] == r"SQL_Generators3"
    
    main()