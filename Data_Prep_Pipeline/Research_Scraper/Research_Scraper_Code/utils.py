"""
Util methods for the scraper
"""
import datetime
import json
import re
import unicodedata
import urllib.parse
import os

import pandas as pd
import pymongo
import requests
import data_prep_helper as helper


def remove_control_characters(s):
    """
    Removes control characters from a string
    :param s: String
    :return: Processed String
    """
    if s is None:
        return None

    # replace all control character with space
    res = "".join(
        ch if unicodedata.category(ch)[0] != "C" else " " for ch in s
    )
    # remove double spaces
    res = " ".join(res.split())

    # search for exceptions that are not covered by the unicodedata.category
    bad_chars = ['\\\\r', '\\\\n', '\\\\t', '\\\\x', '\\\\u', '\\r', '\\n', '\\t', '\\x', '\\u']
    for bad_char in bad_chars:
        if bad_char in res:
            res = res.replace(bad_char, ' ')
            res = " ".join(res.split())
    return res


def find_backslash_r_n_in_middle_of_string(string):
    """
    Finds backslash r and n in the middle of a string (i.e. not at the beginning or end)
    :param string:
    :return: Boolean
    """
    if string is not None and '\r\n' in string:
        if string.index('\r\n') != 0 and string.index('\r\n') != len(string) - 2:
            return True
    return False


def check_if_doi_link(url):
    """
    Checks if given URL is a DOI Link \n
    Source: https://www.medra.org/en/DOI.htm
    :param url: url to check
    :return: Bool
    """

    doi_link_regex = re.compile(r'^(https?:\/\/)?'  # A doi links starts with http:// or https://
                                r'(www\.)?'  # or start with www.
                                r'(doi\.org\/)'  # followed by doi.org/
                                r'10\.'  # DOI suffix starts with '10.'
                                r'\d{4,9}'  # followed by 4-9 digits
                                r'\/[-._;()/:a-zA-Z0-9]+'  # suffix: any character, number, - or . or _ any number of times
                                r'$')

    if doi_link_regex.match(url):
        return True
    else:
        return False


def check_if_doi_number(doi_number):
    """
    Checks if given number matches DOI pattern \n
    Sources: https://www.medra.org/en/DOI.htm, https://www.crossref.org/blog/dois-and-matching-regular-expressions/
    :param doi_number: String
    :return: Bool
    """
    doi_number_regex = re.compile(r'^'  # matching the start
                                  r'10\.'  # DOI suffix starts with '10.'
                                  r'\d{4,9}'  # followed by 4-9 digits
                                  r'\/[-._;()/:a-zA-Z0-9]+'  # followed by suffix: a slash and any number/ character
                                  r'$')

    if doi_number_regex.match(doi_number):
        return True
    else:
        return False


def create_doi_link(doi: str):
    """
    Composes DOI links from DOI numbers
    :param doi: a DOI number
    :return: DOI link to a publication
    """
    # check first if doi is really doi number
    if check_if_doi_number(doi):
        return 'https://doi.org/' + doi
    else:
        return None


def extract_doi_from_doi_link(doi_link):
    """
    Extracts the DOI number from a DOI link
    :param doi_link: DOI link
    :return: DOI number
    """
    doi_number_in_string_regex = re.compile(r'10\.'  # DOI suffix starts with '10.'
                                            r'\d{4,9}'  # followed by 4-9 digits
                                            r'\/[-._;()/:a-zA-Z0-9]+'  # followed by suffix: a slash and any number/ character
                                            r'$')
    doi = doi_number_in_string_regex.search(doi_link).group(0)
    return doi


def resolve_url(url):
    """
    Resolves an url to its final destination
    :param url: url
    :return: resolved url
    """
    try:
        r = requests.head(url, allow_redirects=True, timeout=60)
        return r.url
    except requests.exceptions.ConnectionError as e:
        print(f'[utils.py: get_link] Connection Error: {e}')
        return None


def domain(url):
    """
    Returns the domain-part of an URL
    :param url:
    :return: domain-part of URL
    """
    if url is not None and pd.notna(url):
        return urllib.parse.urlparse(url).netloc  # returns domain
    else:
        return None


def write_results(results, name):
    """
    Writes the results to a json file
    :param name: filename to write
    :param results: Results of scraping, list of dict
    :return: void, writes to file
    """
    if results is not None:
        with open(f'exports/scrapings/{name}.json', 'w') as f:
            json.dump(results, f, indent=4)
            # green background black font
            print(f'\033[1;30;42m{len(results)} results written to {name}.json\033[0m')


def load_and_clean_scraping_results(filename, custom_path=None):
    """
    Reads a json file with scraping results and cleans it by removing None and error rows
    :param custom_path: Specify the custom folder path if you don't want to write it to the default folder
    :param filename: name of file to write
    :return: cleaned results, list of dict
    """
    if custom_path is None:
        path = f'../Application/exports/scrapings/{filename}.json'
    else:
        path = f'{custom_path}/{filename}.json'

    with open(path, 'r') as f:
        scraping_results_imported = json.load(f)

    scraping_results_imported_cleaned = [x for x in scraping_results_imported if
                                         x is not None and x.get('error') is None]

    return scraping_results_imported_cleaned


def load_publications_from_csv():
    """
    Loads the publications from the csv file
    :return: dataframe with publications
    """
    data = 'data/publications_without_abstract.csv'

    with open(data) as f:
        df = pd.read_csv(f, sep=';')
    return df


def get_all_dois(df):
    """
    Gets all the dois from the dataframe and returns them as a list
    :param df:
    :return:
    """
    dois = df['doi']
    # remove NaNs
    dois = dois.dropna()
    dois.tolist()
    return dois


def transform_scrapingdict_searchable_with_key(dict_input):
    """
    Transforms the scraping result dict to a more searchable dict \n
    The id is here the key and the results are directly in the value
    :param dict_input: dict to be transformed
    :return: transformed dict
    """
    dict_new = {x.get('id'): x.get('scraping_result') for x in dict_input}
    return dict_new


# MongoDB

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

def queryMongoDB_publication(query_id):
    """
    Query the publication table from mongoDB and returns the result
    :param query: query to be executed
    :param client: client to connect to
    :param database: database to connect to
    :param column: column to connect to
    :return: result of query
    """
    # credentials will be later stored in a config file or as environment variables
    client = os.getenv('FILLER_ENV_MONGO_URI', "mongodb://localhost:27017")
    # database = "FLK_Data_Lake"
    database = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Data_Lake")
    column = 'publication'

    my_db = access_mongo_db(client, database)

    # query the database
    query = {'id': query_id}
    result = my_db[column].find_one(query)
    # get only following keys: id, cfTitle, doi, cfUri keywords, cfAbstract and drop other cols from dict
    result = {key: result[key] for key in ['id', 'cfTitle', 'doi', 'cfUri', 'keywords', 'cfAbstr']}

    # status debug print
    print(f'[utils.py: queryMongoDB_publication] Query id:{query_id} executed')

    return result


def get_wi_hrchy_data():
    """
    Get the WI entries from cris by using a mongo pipeline on the inst_wi_hrchy collection
    :return: Dataframe with the WI entries
    """
    client = os.getenv('FILLER_ENV_MONGO_URI', "mongodb://localhost:27017")
    # database = "FLK_Data_Lake"
    database = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Web")
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
    result_pipeline = list(my_db['inst_wi_hrchy'].aggregate(pipeline))  # returns mongo cursor

    # convert to dataframe
    df_res = pd.DataFrame.from_records(result_pipeline)
    df_res = df_res.sort_values(by=['id'])

    # drop duplicates
    df_res = df_res.drop_duplicates(subset=['id'])

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


def get_wi_publication_data_df(wi_ids=None):
    """
    Get the WI entries from cris with a mongo pipepline
    Than return the ID of the WI publictions for further work
    Also possible to specify ids to get only the data for these ids
    With the ids get the data from the database in a df
    :param wi_ids: ID of wanted publicaitons, default None -> gets all
    :param publication_ids: Optional: List of publication ids to get the data from
    :return: DF with all WI publications
    """
    if wi_ids is None:
        # get wi-ids
        wi_ids = helper.get_wi_ids()
        # Get the WI Paper and save them in a df and csv

    # get the data from the database
    client = os.getenv('FILLER_ENV_MONGO_URI', "mongodb://localhost:27017")
    # database = "FLK_Data_Lake"
    database = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Data_Lake")
    my_db = access_mongo_db(client, database)
    collection = 'publication'

    # query the data, id must be in wi_publications_ids
    query = {'id': {'$in': wi_ids}}

    df_res = pd.DataFrame.from_records(my_db[collection].find(query))

    # only keep following columns: id, cfAbstr, cfUri, doi, keywords, srcAuthors, cfTitle
    df_res = df_res[
        ['id', 'cfTitle', 'doi', 'cfUri', 'srcAuthors', 'keywords', 'cfAbstr',
         'publYear', 'cfLang']]  # publYear remove unless not needed

    return df_res


def get_collection_df_from_mongo(collection_name):
    # get the data from the database
    client = os.getenv('FILLER_ENV_MONGO_URI', "mongodb://localhost:27017")
    # database = "FLK_Data_Lake"
    database = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Data_Lake")
    my_db = access_mongo_db(client, database)
    collection = my_db[collection_name]
    df_res = pd.DataFrame.from_records(collection.find({}))
    return df_res


def get_time_stamp():
    """
    Returns the current timestamp in the format: YYYY-MM-DD_hhmm (no ":" because of windows)
    :return: String with timestamp
    """
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H%M")
    return timestamp


def safe_push_to_mongo(collection_name, df):
    """
    This function saves the df to the mongoDB collection.
    Checks if the df is already in the collection and only adds the new rows.
    :param collection_name:
    :param df: A df with the data to be saved
    :return:
    """
    status = ''
    # print(f'Initial status: {status}')
    client = os.getenv('FILLER_ENV_MONGO_URI', "mongodb://localhost:27017")
    # database = "FLK_Data_Lake"
    database = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Data_Lake")
    my_db = access_mongo_db(client, database)
    collection = my_db[collection_name]
    # print collection names from db
    # print(f'Collection names: {my_db.list_collection_names()}')

    # check if collection exists
    if collection_name not in my_db.list_collection_names():
        # create collection
        status = 'not_existing'
        print('Collection does not exist, creating collection')
        collection = my_db[collection_name]
        collection.insert_many(df.to_dict('records'))
        print(f'Collection created: {collection_name}')
        print(f'Inserted {len(df)} rows')
        # end method without returning
        return

    else:
        print(f'Collection {collection_name} exists')

    # count rows in collection
    mongo_cursor = collection.find({})
    amount_items_in_collection = len(pd.DataFrame.from_records(mongo_cursor))
    print(f'Amount of items in collection: {amount_items_in_collection}')
    if amount_items_in_collection > 0:
        status = 'existing_not_empty'
        print('Collection exists and is not empty')
    else:
        status = 'existing_empty'
        print('Collection exists but is empty')

    if status == 'existing_not_empty':
        # since not empy, we need to check if there are new rows and push safely

        # get mongo ids
        mongo_ids = pd.DataFrame.from_records(collection.find({}))['id']

        # look for ids that are not in the collection
        ids_not_in_collection = df[~df['id'].isin(mongo_ids)]['id']
        print(f'Amount of new rows: {len(ids_not_in_collection)}')

        # get the rows that are not in the collection
        df_not_in_collection = df[df['id'].isin(ids_not_in_collection)]

        # insert the rows that are not in the collection
        amount_items_not_in_collection = len(df_not_in_collection)
        if amount_items_not_in_collection > 0:
            print(f'Inserting {amount_items_not_in_collection} new rows')
            df_not_in_collection_dict = df_not_in_collection.to_dict('records')
            collection.insert_many(df_not_in_collection_dict)
            return
        else:
            print('No new rows to insert')

    if status == 'existing_empty':
        # since empty, we can just push the df
        print(f'Inserting the {len(df)} rows')
        collection.insert_many(df.to_dict('records'))
        len2 = df.to_dict('records')
        return


def wipe_mongo_collection(collection_name):
    """
    This function wipes the content of a collection for update purposes
    Collection name must be allowed to be wiped
    :param collection_name: collection name
    """
    client = os.getenv('FILLER_ENV_MONGO_URI', "mongodb://localhost:27017")
    # database = "FLK_Data_Lake"
    database = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Data_Lake")
    my_db = access_mongo_db(client, database)
    collection = my_db[collection_name]
    print(f'Wiping collection {collection_name}')
    collection.delete_many({})
    print(f'Collection {collection_name} wiped')
