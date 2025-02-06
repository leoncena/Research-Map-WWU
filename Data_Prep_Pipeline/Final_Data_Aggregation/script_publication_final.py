"""
This script creates the final data set for the publication for frontend and includes filled publication data.
Step 1: Get data from cris (choose with parameter what colloms to get)
Step 2: Merge data with filled data (like picking prepared titles, keywords, abstracts

"""

import os

import numpy as np
import pandas as pd
from pymongo import MongoClient


# Step 1: Get original data from Mongo
def get_original_data(uri) -> pd.DataFrame:
    """
    Get data from mongo and return it as pandas dataframe
    :param uri: mongodb uri
    :return: pandas dataframe
    """
    global df_publications

    client = MongoClient(uri)
    result = client['FLK_Data_Lake']['publication'].find({})
    df_publications = pd.DataFrame.from_records(result)

    print("Original data shape: ", df_publications.shape)

    return df_publications


def get_filled_data(uri) -> pd.DataFrame:
    """
    Get filled data from mongo and return as pd df
    :return: pandas dataframe
    """

    client = MongoClient(uri)
    result = client['FLK_Data_Lake']['publication_filled'].find({})
    df_filled = pd.DataFrame.from_records(result)

    print("Filled data shape: ", df_filled.shape)

    return df_filled


def combine_data(df_publications, df_filled) -> pd.DataFrame:
    """
    Combine original data (controlled by parameter) with filled data.
    Main key is id
    Main attributes (title, url, keywords, cfAbstr, doi and data_source) come from df_filled
    :param df_publications: df with original data
    :param df_filled: df with filled data
    :return: Combined data frame
    """

    # merge data
    df_combined = pd.merge(df_publications, df_filled, on='id', how='right')

    # some attributes need to be chosen from filled or original data (because are duplicates)
    choose_from_filled = ['cfTitle', 'cfUri', 'keywords', 'cfAbstr', 'doi', 'publYear', 'srcAuthors']

    for attribute in choose_from_filled:
        df_combined[attribute] = df_combined[attribute + '_y']
        df_combined.loc[df_combined[attribute + '_y'].isnull(), attribute] = df_combined[attribute + '_x']

    print("Combined data shape: ", df_combined.shape)

    return df_combined


def select_final_data(combined_data, attribute_list):
    """
    Select final data from combined data
    :param attribute_list: list of attributes to select
    :return: final data frame
    """

    # some attributes are mandatory, add them if not in attribute list
    mandatory_attributes = ['id']

    for attribute in mandatory_attributes:
        if attribute not in attribute_list:
            attribute_list.append(attribute)

    # get only attributes from attribute list
    df_final = combined_data[attribute_list]

    # None values should be replaced with None
    df_final = df_final.replace(np.nan, None)

    return df_final


def write_final_publications(df_final, collection_name, db_name, uri):
    """
    Write final publications to mongo
    :param df_final: final data frame
    :param collection_name: name of collection
    :param db_name: name of db
    :param uri: uri of mongo
    :return: None
    """
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]

    # delete old data
    collection.delete_many({})

    # write new data
    collection.insert_many(df_final.to_dict('records'))


def create_and_push_final_data(uri, attribute_list, collection_name, db_name):
    """
    Create final data and push it to mongo
    :param uri: uri of mongo
    :param attribute_list: list of attributes to select
    :param collection_name: name of collection
    :param db_name: name of db
    :return: None
    """
    df_publications = get_original_data(uri)
    print('Loaded original data from Mongo')
    df_filled = get_filled_data(uri)
    print('Loaded filled data from Mongo')
    df_combined = combine_data(df_publications, df_filled)
    # print df_combined col names
    print(df_combined.columns.tolist())
    print('Combined data generated')
    df_final = select_final_data(df_combined, attribute_list)
    print('Final data generated')
    write_final_publications(df_final, collection_name, db_name, uri)
    print("Pushed to Mongo: ", collection_name, " in db: ", db_name)
    return df_final


def add_wwu_authors(collection, target_db, uri):
    """
    Add wwu authors for each publication
    :return: None
    """
    client = MongoClient(uri)
    db = client[target_db]
    collection = db[collection]
    publications = collection.aggregate([
        {
            '$lookup': {
                'from': 'person_publications',
                'localField': 'id',
                'foreignField': 'publication_id',
                'as': 'authorConnections'
            }
        }, {
            '$unset': 'authorConnections.publication_id'
        }, {
            '$lookup': {
                'from': 'person',
                'localField': 'authorConnections.person_id',
                'foreignField': 'id',
                'as': 'authorList'
            }
        }, {
            '$unset': [
                'authorConnections'
            ]
        }
    ])

    publications = list(publications)
    publications = prepare_authors_in_publications(publications)
    collection.delete_many({})
    collection.insert_many(publications)


def prepare_authors_in_publications(publications):
    """
    Prepare authors in publications for frontend.
    Removing unnecessary attributes and adding name attribute
    :param publications:
    :return: list of prepared publications
    """
    prepared_publications = []
    for publication in publications:
        prepared_publication = {k: None if not v else v for k, v in publication.items()}
        for key, value in prepared_publication.items():
            # Replace NaN with empty string for Meilisearch
            if key == "authorList" and type(value) is list:
                for author in value:
                    for k in list(author.keys()):
                        # Remove unnecessary author attributes
                        if k not in ['id', 'cfFamilyNames', 'cfFirstNames']:
                            del author[k]
                    author['Name'] = author['cfFirstNames'] + " " + author['cfFamilyNames']
        prepared_publications.append(prepared_publication)
    return prepared_publications


def export_persons_to_flk_web():
    uri = os.getenv('MONGODB_TO_URI', "mongodb://localhost:27017")
    add_wwu_authors('publication_filled', 'FLK_Data_Lake', uri)
    attribute_list_publications_final = ['id', 'authorList', 'cfTitle', 'cfUri', 'keywords', 'cfAbstr', 'doi', 'data_source',
                                     'title_nlp', 'srcAuthors',
                                     'keywords_nlp', 'abstract_nlp', 'publicationType', 'publYear', 'similar_publications']
    result = create_and_push_final_data(uri, attribute_list_publications_final, 'publications', 'FLK_Web')

if __name__ == '__main__':
    # Here one can create several final data sets with different attributes for frontend components
    export_persons_to_flk_web()
