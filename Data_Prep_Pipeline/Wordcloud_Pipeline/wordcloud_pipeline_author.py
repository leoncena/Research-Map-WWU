"""
This script prepares the data from a person in such a way that all their publications are assigned.
The publication data is filtered with Spacy and made available as a Wordcloud ready for visualization
"""

# load Data from Database
import os
import pymongo
import spacy
import en_core_web_sm
import data_prep_helper as helper
from pipeline_helper import access_mongo_db_person_data,complete_push_to_mongo_data_lake

nlp = en_core_web_sm.load()
nlp = spacy.load("en_core_web_sm")

CLIENT = os.getenv('FILLER_ENV_MONGO_URI', "mongodb://localhost:27017")
DATABASE_FLK_DATA_LAKE = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Data_Lake")


def get_author_publication_data(pub_author):
    """
    The value strings of a publication, if they exist, are combined into one large string. This enriches the word cloud.
    :param pub_author: publications by one author
    :return: result
    """
    result = ""

    if pub_author['title_nlp'] != '' and type(pub_author['title_nlp']) == str:
        result += " " + pub_author['title_nlp']

    if pub_author['abstract_nlp'] != '' and type(pub_author['abstract_nlp']) == str:
        result += " " + pub_author['abstract_nlp']

    if pub_author['keywords'] != '' and type(pub_author['keywords']) == str:
        result += " " + pub_author['keywords']

    return result


def extract_publication_info(persons):
    """
       In this function, all data on an author is filtered, i.e. freed from stop words and then saved in a
       list with the following format.
       A list of dictionaries is returned in the format: [{"author_id" : "123232",
                                                          "publications" : [{"publication_id" : "213233",
                                                                             "data_for_wordcloud": "design, software, ...",
                                                                             "publYear": "2022"}},...]
      :param persons: Data from persons collection
      :return: publication_info
    """

    wi_ids = helper.get_wi_ids()
    publication_info = []
    for person in persons:
        author_id = person['id']

        publication_ids = helper.get_publications_for_person(int(author_id))
        publication_ids = [str(pub_id) for pub_id in publication_ids]
        # only show wi publications
        publication_ids = [pub_id for pub_id in publication_ids if pub_id in wi_ids]

        # List of publications by author
        list_pub_author = []
        # Prepare publication data per person
        for pub_id in publication_ids:
            my_client = pymongo.MongoClient(CLIENT)
            db = my_client[DATABASE_FLK_DATA_LAKE]
            pub_author = db['publication_filled'].find_one({'id': pub_id})
            my_client.close()
            # Make a string from the publication data
            string_of_publication = get_author_publication_data(pub_author)

            # Remove commas, and other unnecessary things from string
            data_for_wordcloud = preprocess_documents(string_of_publication)
            # sub eintrag für publication list
            pub_dict = {
                'publication_id': pub_author['id'],
                'data_for_wordcloud': data_for_wordcloud,
                'publYear': int(pub_author['publYear'])
            }

            list_pub_author.append(pub_dict)

        # Merge entry from one person
        actual_entry = {
            "author_id": author_id,
            "publications": list_pub_author}

        publication_info.append(actual_entry)

    return publication_info


def preprocess_documents(text):
    """
    Function to clean the Sting of a publication from Stopwords
    :param text:
    :return: preprocessed_text as String, all words split with commas
    """
    doc = nlp(text)
    tokens = [token for token in doc if not token.is_punct and not token.is_space]
    nouns_verbs = [token.lemma_.lower() for token in tokens if
                   not token.is_stop and token.is_alpha]  # token.pos_ in ['NOUN', 'VERB'] and
    preprocessed_text = ', '.join(nouns_verbs)
    return preprocessed_text


# Functions for exporting the data to the database:
def preprocess_data_for_wordcloud(collection_name):
    # Import publication Data
    print("Processing of wordcloud data has started...")
    data_form_persons = access_mongo_db_person_data()
    print("Data Import is completed")

    # Dictionary erstellen
    dictionary_with_author = extract_publication_info(data_form_persons)

    print("Data processing is complete")
    print("Load data to Database: ")
    # The third parameter specifies which collection may be deleted for writing with new data (security mechanism)
    complete_push_to_mongo_data_lake(collection_name, dictionary_with_author, collection_name)
    print(" ")
    print("Execution was a success!")


pass

if __name__ == "__main__":
    # Run the pipeline
    preprocess_data_for_wordcloud('publication_wordcloud_data_author')
