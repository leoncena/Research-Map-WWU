"""
The idea here is to suggest a selection of articles to the user with similar articles.
The results from the Top2Vec model are now used for this. Since one can say that all publications assigned to a certain topic are similar to each other, since they have a certain fit to the topic words, the surrounding n articles are assigned to an article in the assignment as similar articles.
"""

import os
import sys

pipeline_helper_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data_Prep_Pipeline'))
sys.path.append(pipeline_helper_path)
# load Data from Database


from top2vec import Top2Vec
import pymongo

import data_prep_helper as helper
from pipeline_helper import get_wi_publication_data_df, build_sting_per_publication, complete_push_to_mongo_data_lake


def build_model(publication_data):
    """
    Build and train a Model based on the given Data using Top2Vec algorithm
    :param model_path: model_path
    :param publication_data:
    :return: trained model
    """
    # create top2vec model
    model = Top2Vec(publication_data[1], document_ids=publication_data[0])

    return model


# Super function that aggregates everything
def related_documents_by_id(model):
    """
     This function creates a list of related documents per topic vector
     :param model: top2vec model
     :return: nested list of all documents
    """
    # Ermitteln der Anzahl an Überschriften
    number_of_topics = get_topic_sizes(model)

    all_topic_groups = []

    for actual_topic in range(number_of_topics):
        topic_group_list = get_all_document_id_list(model,
                                                    actual_topic).tolist()

        topic_group_all_int = list(map(int, topic_group_list))

        all_topic_groups.append(topic_group_all_int)

    return all_topic_groups


def get_topic_sizes(model):
    """
    A list with the number of documents per topic is returned
    :param model: trained data model
    :return: pandas.series with the counts per heading
    """
    return model.topic_sizes.size


def get_all_document_id_list(model, topic_no):
    '''
    Returns all Document_ids that can be assigned to topic_no
    :param model: trained data model
    :param topic_no: topic
    :return: document_ids
    '''

    number_of_publications = get_topic_sizes_by_id(model,
                                                   topic_no)

    documents, document_scores, document_ids = model.search_documents_by_topic(topic_num=topic_no,
                                                                               num_docs=number_of_publications)

    return document_ids


def get_topic_sizes_by_id(model, id):
    """
    This function specifies the number of assigned publications for a topic_id from the Top2Vec model
    :param model: trained data model
    :param id: the ID for the entered data
    :return: returns the number of items per topic
    """
    data = model.topic_sizes
    return data[id]


def get_related_documents(list_of_article_group):
    """
    Input is a nested list of all ids
    which calculates all that are similar and returns a dictionary in which each publicationID is assigned a dictionary
    in which each publication_Id is assigned 8 related articles
    :return: simular_article_all
    """
    # Simular Articles per article
    no_of_articles = 8

    # dictionary with result
    simular_article_all = []

    index = 0

    for group_of_articles in list_of_article_group:
        for position_in_group in range(len(group_of_articles)):
            article_id = group_of_articles[position_in_group]
            simular_articles_list = compute_simular_articles(group_of_articles,
                                                             position_in_group,
                                                             no_of_articles)

            simular_articles_list_str = [str(number) for number in simular_articles_list]

            simular_article_all.append({'id': str(article_id), 'simular_publications': simular_articles_list_str})
            index += 1

    return simular_article_all


def compute_simular_articles(group_of_articles, position_in_group, no_of_articles):
    """
    For each element, this function returns a list of n publication_ids that are a similar distance from the center of the cluster.
    The input is a list of ids sorted in descending order of fit.
    The n/2 elements before the current element and n/2 after it. If it is the first element,
    for example, the n elements behind it are returned
    :param group_of_articles: a list from a subject area
    :param position_in_group: position at which the element is located
    :param no_of_articles: number of similar items to be specified
    :return: list with no_of_articles ids of similar publications
    """
    length_of_article_list = len(group_of_articles)

    # If there are fewer articles than the no_of_articles calls for
    if (no_of_articles > length_of_article_list):
        simular_articles_list = return_all_except_by_id(group_of_articles,
                                                        position_in_group)
        return simular_articles_list

    # Executed when there are fewer items before the item
    if (no_of_articles / 2 > position_in_group):

        # If you only look at the first element
        if (position_in_group == 0):
            simular_articles_list = group_of_articles[1: no_of_articles + 1]
            return simular_articles_list
        else:
            # Serve on second part
            surcharge_part_two = (no_of_articles / 2) - position_in_group

            # The first part of the list, from the 0 element to the current element
            part_one = group_of_articles[0: position_in_group]
            # Second part of the list from the current element to the end with markup
            part_two = group_of_articles[
                       position_in_group + 1: int(position_in_group + 1 + (no_of_articles / 2) + surcharge_part_two)]

            # Elements before and after the current element are merged into one
            merged_result_list = make_one_list([part_one, part_two])
            return merged_result_list

    # Before and after the current element there are enough elements that can be selected
    if ((position_in_group + 1) - (no_of_articles / 2) > 0 and ((position_in_group + 1) + (
            no_of_articles / 2)) <= length_of_article_list):  # Hier wurden die Klammern verändert

        # Find the elements before the current element
        part_one = group_of_articles[int(position_in_group - (no_of_articles / 2)):position_in_group]
        # Finding the elements after the current element
        part_two = group_of_articles[position_in_group + 1: int(position_in_group + 1 + (no_of_articles / 2))]

        # Elements before and after the current element are merged into one
        merged_result_list = make_one_list([part_one, part_two])
        return merged_result_list

    # There is not enough space behind the current element, so add elements to the second part of the list
    if (length_of_article_list - no_of_articles / 2) < position_in_group + 1:
        surcharge_part_one = (no_of_articles / 2) - (length_of_article_list - (position_in_group + 1))

        # Find the elements before the current element
        part_one = group_of_articles[
                   int((position_in_group - (no_of_articles / 2) - surcharge_part_one)): position_in_group]
        # Finding the elements after the current element
        part_two = group_of_articles[position_in_group + 1: length_of_article_list]

        # Elements before and after the current element are merged into one
        merged_result_list = make_one_list([part_one, part_two])
        return merged_result_list


def make_one_list(nested_list):
    """
    This function converts a simply nested list into a list that is no longer nested
    :param nested_list:
    :return: flat list
    """
    flat_list = []
    for item in nested_list:
        # appending elements to the flat_list
        flat_list += item
    return flat_list


def return_all_except_by_id(lst, index):
    """
    The function returns all elements from a list in a list except the element with the specified index
    :param lst:
    :param index:
    :return:list_without_id
    """
    return lst[:index] + lst[index + 1:]


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


def merge_db_final_format():
    """
    The ones that are obtained in this script are stored as an additional column in the Publication_filled
    collection in the FLK_Data_Lake database. This is necessary to enable easier access on the front end
    :return:
    """
    client = os.getenv('FILLER_ENV_MONGO_URI', "mongodb://localhost:27017")
    database = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Data_Lake")

    client = access_mongo_db(client, database)

    client['publication_filled'].aggregate([
        {
            '$lookup': {
                'from': 'data_for_related_docs',
                'localField': 'id',
                'foreignField': 'id',
                'as': 'relatedDocs'
            }
        }, {
            '$addFields': {
                'similar_publications': {
                    '$first': '$relatedDocs.simular_publications'
                }
            }
        }, {
            '$unset': 'relatedDocs'
        }, {
            '$out': 'publication_filled'
        }
    ])


def find_related_documents(collection_name):
    """
    This function controls the entire flow of the related documents pipeline.
    :param collection_name:
    :return:
    """
    print("Process has started")
    # load publication Data from MongoDB
    columns = ['id', 'title_nlp', 'keywords_nlp', 'abstract_nlp', 'publYear']
    publication_data = get_wi_publication_data_df(columns)
    print("Loaded data from database FLK_Data_Lake from collection publication_filled")

    # preprocess titel,abstract,keywords per publication

    string_per_publication = build_sting_per_publication(publication_data)
    print("Data has been preprocessed")
    # build model
    print("Start generating Top2Vec model")
    model = build_model(string_per_publication)

    nested_list = related_documents_by_id(model)

    print("List of all publications created")
    # search from the 8 related publications
    related_publication_dict = get_related_documents(nested_list)

    print("Similar articles were assigned to each index")
    # Safe data in Database
    # The third parameter specifies which collection may be deleted for writing with new data (security mechanism)
    complete_push_to_mongo_data_lake(collection_name, related_publication_dict, collection_name)
    print(
        "Data was successfully written to the database {} in the collection {}".format("FLK_Web", collection_name))
    merge_db_final_format()
    print(
        "Data was merged into database: {}, collection: {} successfully, column: {}".format("FLk_Data_Lake",
                                                                                            "publication_filled",
                                                                                            "relatedDocs"))
    print("Execution was a success !")


if __name__ == "__main__":
    find_related_documents(collection_name='data_for_related_docs')
