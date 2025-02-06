"""
Functions are bundled in this script, in particular accessing and loading data from databases and saving results to databases
"""

import os
import pymongo
import pandas as pd
import data_prep_helper as helper

CLIENT = os.getenv('FILLER_ENV_MONGO_URI', "mongodb://localhost:27017")
DATABASE_FLK_DATA_LAKE = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Data_Lake")
DATABASE_FLK_WEB = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Web")


# Function to access Mongo Database and load Data
def access_mongo_db(client, database):
    """
    Method to access the mongoDB
    :param client: Client mongoDB
    :param database: Name of database
    :return: connection to database
    """
    # connect to mongoDB
    my_client = pymongo.MongoClient(client)
    my_db = my_client[database]
    return my_db


def get_wi_publication_data_df(column_labels: list, wi_ids=None):
    """
    Get the WI entries from cris with a mongo pipepline
    Than return the ID of the WI publictions for further work
    Also possible to specify ids to get only the data for these ids
    With the ids get the data from the database in a df
    :param column_labels:
    :param wi_ids: ID of wanted publicaitons, default None -> gets all
    :param publication_ids: Optional: List of publication ids to get the data from
    :return: DF with all WI publications
    """
    if wi_ids is None:
        # get wi-ids
        wi_ids = get_wi_ids()
        # Get the WI Paper and save them in a df and csv

    # get the data from the database
    client = CLIENT
    # database = "FLK_Data_Lake"
    database = DATABASE_FLK_DATA_LAKE
    my_db = access_mongo_db(client, database)
    collection = 'publication_filled'

    # query the data, id must be in wi_publications_ids
    query = {'id': {'$in': wi_ids}}

    df_res = pd.DataFrame.from_records(my_db[collection].find(query))

    # only keep following columns: id, cfAbstr, cfUri, doi, keywords, srcAuthors, cfTitle
    df_res = df_res[column_labels]  # select only the required attributes

    return df_res


def get_wi_ids():
    """
    Get the WI entries from cris with a mongo pipepline
    Than return the ID of the WI publictions for further work
    :return: List of ids
    """
    wi_df = get_wi_hrchy_data()

    # get col 'id' from wi_df as list
    wi_ids = wi_df['id'].tolist()
    return wi_ids


def get_wi_hrchy_data():
    """
    Get the WI entries from cris by using a mongo pipeline on the inst_wi_hrchy collection
    :return: Dataframe with the WI entries
    """
    client = CLIENT
    # database = "FLK_Data_Lake"
    database = DATABASE_FLK_DATA_LAKE
    my_db = access_mongo_db(client, database)

    # mongo pipeline to unwind the hierarchy and get the data ( like a melt)
    pipeline = [
        {
            '$unwind': {
                'path': '$children'
            }
        }, {
            '$replaceRoot': {
                'newRoot': '$children'
            }
        }, {
            '$unwind': {
                'path': '$children'
            }
        }, {
            '$replaceRoot': {
                'newRoot': '$children'
            }
        }, {
            '$unwind': {
                'path': '$children'
            }
        }, {
            '$replaceRoot': {
                'newRoot': '$children'
            }
        }
    ]
    result_pipeline = my_db['inst_wi_hrchy'].aggregate(pipeline)  # returns mongo cursor

    # convert to dataframe
    df_res = pd.DataFrame.from_records(result_pipeline)
    df_res = df_res.sort_values(by=['id'])

    # drop duplicates
    df_res = df_res.drop_duplicates(subset=['id'])

    return df_res


## Functions to write on DB


# Functions for exporting the data to the database:
def access_mongo_db(client, database):
    """
    Method to access the mongoDB
    :param client: Client mongoDB
    :param database: Name of database
    :return: connection to database
    """
    # connect to mongoDB
    my_client = pymongo.MongoClient(client)
    my_db = my_client[database]
    return my_db


def access_mongo_db_person_data():
    """
    With this function we pull the collection person Data
    :return:
    """

    wi_persons = helper.get_wi_persons()
    wi_persons = [str(item) for item in wi_persons]
    # get the data from the database
    client = CLIENT
    # database = "FLK_Data_Lake"
    database = DATABASE_FLK_DATA_LAKE
    my_db = access_mongo_db(client, database)
    collection = my_db['person'].find({"id": {"$in": wi_persons}})

    # Daten aus der Sammlung abrufen
    data = [item for item in collection]

    return data


# Function to join strings together
def build_sting_per_publication(publication_data):
    """
    Function creates a uniform string from the given information per item.
    The title, the abstract and the keywords that were specified for a publication are used for this.
    In order to enable later identification of the article, the ID is also recorded
    the variable token checks whether an entry is created, if this is the case, the CRIS ID is transmitted.
    a list containing two partial lists is returned. this is necessary because it is the only way to pass the IDs to the Top2Vec method
    :param publication_data: dataframe with the publication_data
    :return:[publication_as_str,document_ids]
    """
    publications_as_string = []
    document_ids = []

    for index, row in publication_data.iterrows():
        actual_entry = []
        token = False

        if (row['title_nlp'] != '' or type(row['title_nlp']) == str):
            token = True
            title_as_str = extract_str(row, 'title_nlp')
            actual_entry.append(title_as_str)

        if (row['abstract_nlp'] != '' or type(row['abstract_nlp']) == str):
            token = True
            abstract_as_str = extract_str(row, 'abstract_nlp')
            actual_entry.append(abstract_as_str)

        if (row['keywords_nlp'] != '' or type(row['keywords_nlp']) == str):
            token = True
            keywords_as_str = extract_str(row, 'keywords_nlp')
            actual_entry.append(keywords_as_str)

        complete_String = ' '.join(actual_entry)
        publications_as_string.append(complete_String)

        # publ_id hinzufügen
        if (token == True):
            document_ids.append(row['id'])

    return [document_ids, publications_as_string]


def extract_str(row, column_name: str):
    """
    Makes a string from the values in a row of a column
    :return: String from one line
    """
    actual_abstr = row[column_name]
    return str(actual_abstr)


# Functions to write to database


def complete_push_to_mongo_web(collection_name, data_as_dict, allowed_collection):
    """
    This function saves the df to the mongoDB collection.
    Overwrites the old content and saves complete new content.
    It loads the data to the database FLK_Web
    :param collection_name: name of the collection to which the data should be written
    :param df: A df with the data to be saved
    :param allowed_collection: List of collections that may be deleted
    :return:
    """
    status = ''
    print(f'Initial status: {status}')
    client = CLIENT
    database = DATABASE_FLK_WEB
    my_db = access_mongo_db(client, database)
    collection = my_db[collection_name]

    print('Collection exist, wipe collection')
    wipe_mongo_collection_web(collection_name, allowed_collection=allowed_collection)
    print('Load new Collection data')
    collection.insert_many(data_as_dict)


def wipe_mongo_collection_web(collection_name, allowed_collection):
    """
    This function wipes the content of a collection for update purposes
    Collection name must be allowed to be wiped
    :param collection_name: collection name
    :param allowed_collection: List of collections that may be deleted
    """
    allowed_collections = allowed_collection
    if collection_name not in allowed_collections:
        print(f'Collection {collection_name} not allowed to be wiped')
        return

    client = CLIENT
    database = DATABASE_FLK_WEB
    my_db = access_mongo_db(client, database)
    collection = my_db[collection_name]
    print(f'Wiping collection {collection_name}')
    collection.delete_many({})
    print(f'Collection {collection_name} wiped')


def complete_push_to_mongo_data_lake(collection_name, data_as_dict, allowed_collection):
    """
    This function saves the df to the mongoDB collection.
    Overwrites the old content and saves complete new content.
    It loads the data to the database FLK_Data_Lake
    :param collection_name: name of the collection to which the data should be written
    :param df: A df with the data to be saved
    :return:
    """
    status = ''
    print(f'Initial status: {status}')
    client = CLIENT
    database = DATABASE_FLK_DATA_LAKE
    my_db = access_mongo_db(client, database)
    collection = my_db[collection_name]

    print('Collection exist, wipe collection')
    wipe_mongo_collection_data_lake(collection_name, allowed_collection=allowed_collection)
    print('Load new Collection data')
    collection.insert_many(data_as_dict)


def wipe_mongo_collection_data_lake(collection_name, allowed_collection):
    """
    This function wipes the content of a collection for update purposes
    Collection name must be allowed to be wiped
    :param collection_name: collection name
    :param allowed_collection: List of collections that may be deleted
    """
    allowed_collections = allowed_collection
    if collection_name not in allowed_collections:
        print(f'Collection {collection_name} not allowed to be wiped')
        return

    client = CLIENT
    database = DATABASE_FLK_DATA_LAKE
    my_db = access_mongo_db(client, database)
    collection = my_db[collection_name]
    print(f'Wiping collection {collection_name}')
    collection.delete_many({})
    print(f'Collection {collection_name} wiped')
