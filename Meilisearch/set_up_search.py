import meilisearch
import os
import pymongo as pm
import time
import math

MONGODB_TO_URI = os.getenv('PIPELINE_ENV_MONGODB_TO_URI',
                           "mongodb://localhost:27017/")
MONGODB_TO_DB = os.getenv("MONGODB_TO_DB", "FLK_Web")
MEILISEARCH_URI = os.getenv('PIPELINE_ENV_MEILISEARCH_URI', 'http://10.14.29.19:443')
MEILISEARCH_INDEX_NAME = "publications"
MEILISEARCH_API_KEY = os.getenv('PIPELINE_ENV_MEILISEARCH_API',
                                'd503d32d437f94deb8260772ded7ea75322fc1c7b134b9afd5e6b515bdedf207')


def set_ranking_order(index_name: str, ranking_order: list):
    """
    Update ranking order of index attributes.

    :param index_name: name of index
    :param ranking_order: list of ranking order
    :return: None
    """
    index = search_client.get_index(index_name)
    index.update_settings({
        'rankingRules': ranking_order
    })


def set_sortable_attributes(index_name: str, sortable_attributes: list):
    """
    Update sortable attributes of index.

    :param index_name: name of index
    :param sortable_attributes: list of sortable attributes
    :return: None
    """
    index = search_client.get_index(index_name)
    index.update_settings({
        'sortableAttributes': sortable_attributes
    })
    wait_for_execution(index_name, 'documentAdditionOrUpdate')


def set_filterable_attributes(index_name: str, filterable_attributes: list):
    """
    Update filterable attributes of index.

    :param index_name: name of index
    :param filterable_attributes: list of filterable attributes
    :return: None
    """
    index = search_client.get_index(index_name)
    index.update_settings({
        'filterableAttributes': filterable_attributes
    })
    wait_for_execution(index_name, 'documentAdditionOrUpdate')


def wait_for_execution(index_id: str, task_type: str):
    """
    Wait for asynchronous tasks to finish.
    :param index_id: id of index
    :param task_type: type of task
    :return:
    """
    statuses = search_client.get_tasks(
        {'indexUids': [index_id], 'types': [task_type], 'statuses': ['enqueued', 'processing']})
    while len(statuses['results']) > 0:
        time.sleep(1)
        statuses = search_client.get_tasks(
            {'indexUids': [index_id], 'types': [task_type], 'statuses': ['enqueued', 'processing']})


def create_index(index_name: str, primary_key: str):
    """
    Create index.

    :param index_name: name of index
    :param primary_key: primary key of index
    :return: None
    """
    search_client.create_index(index_name, {'primaryKey': primary_key})
    wait_for_execution(index_name, 'indexCreation')


def delete_index(index_name: str):
    """
    Delete index.

    :param index_name: name of index
    :return: None
    """
    index = search_client.get_index(index_name)
    index.delete()
    wait_for_execution(index_name, 'indexDeletion')


def add_documents(index_name: str, documents: list):
    """
    Append documents to index.

    :param index_name: name of index
    :param documents: list of documents
    :return: None
    """
    index = search_client.get_index(index_name)
    index.add_documents(documents)
    wait_for_execution(index_name, 'documentAdditionOrUpdate')


def replace_nan_with_empty_string(documents: list):
    """
    Replace nan values with empty strings and removes the _id field.
    :param documents: list of dicts
    :return: list of dicts with empty strings instead of nan values
    """
    prepared_publications = []
    for publication in documents:
        prepared_publication = {k: v or "" for (k, v) in publication.items()}
        for key, value in prepared_publication.items():
            # Replace NaN with empty string for Meilisearch
            if type(value) is float and math.isnan(value):
                prepared_publication[key] = ""
        prepared_publications.append(prepared_publication)
        prepared_publication.pop('_id', None)
    return prepared_publications


search_client = meilisearch.Client(MEILISEARCH_URI, MEILISEARCH_API_KEY)
indexes = search_client.get_indexes()
for index in indexes['results']:
    delete_index(index.uid)

create_index(MEILISEARCH_INDEX_NAME, 'id')
index = search_client.get_index(MEILISEARCH_INDEX_NAME)

client = pm.MongoClient(MONGODB_TO_URI)
db = client[MONGODB_TO_DB]
collection = db["publications"]
publications = list(collection.find({}))
publications = replace_nan_with_empty_string(publications)
add_documents(MEILISEARCH_INDEX_NAME, publications)

client.close()
# Filter by publication year, language, and publication type by facets
set_filterable_attributes(MEILISEARCH_INDEX_NAME, ['publYear', 'publicationType'])
set_sortable_attributes(MEILISEARCH_INDEX_NAME, ['publYear', 'publicationType'])
