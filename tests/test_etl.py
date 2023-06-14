import os
import sys
sys.path.append(os.getcwd())
from src.csv_to_json import merge_datasets, clean_dataset, transform_dataset
import pandas as pd

def test_merge():
    # intialise data of lists.
    comic_data = {'comicID':[1, 2, 3],
            'title':['title1', 'title2', 'title3']}

    character_data = {'characterID':[11, 12, 13],
            'name':['char11', 'char12', 'char13']}

    characters_comic_data = {'comicID':[1, 1, 2, 3, 3],
            'characterID':[11,13,13,11,12]}

    expected_data = {'comicID':[1, 1, 2, 3, 3],
                    'title':['title1', 'title1', 'title2','title3', 'title3'],
                    'characterID':[11,13,13,11,12],
                    'name':['char11', 'char13', 'char13','char11', 'char12']}
    # Create DataFrame
    df1 = pd.DataFrame(comic_data)
    df2 = pd.DataFrame(characters_comic_data)
    df3 = pd.DataFrame(character_data)
    exp_df = pd.DataFrame(expected_data)

    df = merge_datasets(df1,df2,df3)
    assert df.equals(exp_df)

def test_cleansing():
    # intialise data of lists.
    pd.set_option('display.max_colwidth', None)
    input_data = {'comicID':[1, 1, 2],
                    'title':["title (1990)", "title (1998) #1", 'title2 (2023)'],
                    'description':["Dec'1", "example (1998) #1", 'test desc'],
                    'issueNumber':[10.0,20.0,30],
                    'characterID':[11,13,13],
                    'name':['char11', 'char13', 'char13']}
    # Create DataFrame
    input_df = pd.DataFrame(input_data)

    exp_data = {'comicID':[1, 1, 2],
                    'title':["title (1990)", "title (1998) #1", 'title2 (2023)'],
                    'description':["Dec1", "example (1998) #1", 'test desc'],
                    'issueNumber':[10,20,30],
                    'characterID':[11,13,13],
                    'name':['char11', 'char13', 'char13'],
                    'year' : [1990, 1998, 2023]}
    
    exp_df = pd.DataFrame(exp_data)  
    exp_df["issueNumber"] = exp_df["issueNumber"].astype(int)
    exp_df["characterID"] = exp_df["characterID"].astype(int)
    exp_df["year"] = exp_df["year"].astype(int)
    
    df = clean_dataset(input_df)
    assert df.equals(exp_df)