import argparse
from collections import namedtuple, Counter

import numpy as np
import pandas as pd

import os

def replace_missing_list_column_values(df, col_name):
    """Replace nans with empty list in list type columns

        * Features such as genres, awards, characters etc are of type 'list'.
        * The default value for missing values for these columns should be an
          empty list instead of nan/None
        * We cannot use fillna() since it does not accept a list as a value

        Mutates the dataframe in place.
    """
    missing_values = df[col_name].isnull()
    df.loc[missing_values, col_name] = pd.Series(
        [
            [] for _ in range(missing_values.count())
        ])


def one_hot_encode_genres(df, k=30):
    """One-hot encodes genres as columns, retaining the k most common genres.

        Mutates the dataframe in place.
    """
    genre_counts = Counter((genre for row_genres in df.genres for genre in row_genres))

    for genre, genre_count in genre_counts.most_common(k):
        df[genre] = df.genres.apply(lambda g: genre in g)

COUNT = 0
def breakdown_publish_date(df):
    global COUNT
    """Adds publish_year, publish_month and publish_day as individual columns"""
    # print(df['publishDate'])
    # publish_dates = pd.to_datetime(
    #     df['publishDate'],#df['publish_date'],
    #     # format="%Y-%m-%d %H:%M:%S",
    #     utc=False,
    #     #infer_datetime_format=True,
    #     errors='coerce')
    try:
        df['publishDate'] = pd.to_datetime(df['publishDate'], unit='ms').dt.strftime('%Y-%m-%d')
    except: 
        COUNT += 1
        print(COUNT)
        
    # df['publish_year'] = publish_dates.apply(lambda k: k.year)
    # df['publish_month'] = publish_dates.apply(lambda k: k.month)
    # df['publish_day'] = publish_dates.apply(lambda k: k.day)

###################################
######### For script mode #########
###################################

def parse_args():
    parser = argparse.ArgumentParser(description='Aggregator script to clean and transform Goodreads data')
    parser.add_argument('-t', '--entityType', help='Type of data; currently author or book', required=True)
    parser.add_argument('-f', '--filenames', nargs='+', help='Space separated JSONLINES files extracted from Goodreads', required=True)
    parser.add_argument('-o', '--output', help='Output CSV file name to which data will be extracted', required=True)
    return parser.parse_args()

def main():
    args = parse_args()

    assert args.entityType in ['author','book']
    
    if 'all' in map(str.lower,args.filenames):
        
        # Get the current directory
        current_directory = os.getcwd()

        # List all files in the current directory
        all_files = os.listdir(current_directory)

        # Filter files that start with "author_" and end with ".jl"
        target_files = [file for file in all_files if file.startswith(f"{args.entityType}_") 
                                and file.endswith(".jl")]

        args.filenames = target_files
     
    dfs = [pd.read_json(filename, lines=True) for filename in args.filenames]
    df = pd.concat(dfs)
    df = df.drop_duplicates(subset=['url'])

    replace_missing_list_column_values(df, 'genres')
    
    if args.entityType == 'book':
        replace_missing_list_column_values(df, 'awards')

    one_hot_encode_genres(df)
    if args.entityType == 'book':
        breakdown_publish_date(df)

        df['num_awards'] = df['awards'].apply(len)

    print(df.head())

    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
