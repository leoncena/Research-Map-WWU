"""
In this script, with the help of Top2Vec , each document ID is the 3 first i.e. also the strongest topic words from the Top2Vec model.
They then serve as 'artificial keywords' and are displayed in the publication search if no real keywords are available.
"""

# load Data from Database
import os
import spacy
import en_core_web_sm
from pipeline_helper import complete_push_to_mongo_data_lake,build_sting_per_publication,get_wi_publication_data_df
nlp = en_core_web_sm.load()
nlp = spacy.load("en_core_web_sm")

CLIENT = os.getenv('FILLER_ENV_MONGO_URI', "mongodb://localhost:27017")
DATABASE_DATA_LAKE = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Data_Lake")
DATABASE_FLK_WEB = os.getenv('FILLER_ENV_MONGO_DATABASE_DATA_LAKE', "FLK_Web")


def preprocess_documents(text):
    """
    In this function, all nouns and verbs are filtered out of a string in order to only display them in a word cloud in order to get a clean display
    :param text: String from which all non-nouns and non-verbs are filtered
    :return: String containing only verbs and nouns
    """
    doc = nlp(text)
    tokens = [token for token in doc if not token.is_punct and not token.is_space]
    nouns_verbs = [token.lemma_.lower() for token in tokens if
                   token.pos_ in ['NOUN', 'VERB'] and not token.is_stop and token.is_alpha]
    preprocessed_text = ', '.join(nouns_verbs)
    return preprocessed_text


def clean_string(string_per_publication):
    """
    In this function, strings are prepared for display in a wordcloud
    :param string_per_publication:
    :return: zipped list in which a publication id is concatenated with a fully processed string
    """

    list_with_ids = string_per_publication[0]
    list_with_strings = string_per_publication[1]
    list_with_clean_strings = []

    for count in range(len(list_with_strings)):
        # cleaned_string = prepare_data_for_wordcloud(list_with_strings[count])
        cleaned_string = preprocess_documents(list_with_strings[count])
        # Join splitted Data
        list_with_clean_strings.append(cleaned_string)

    # change data format
    merged_list = [list_with_ids, list_with_clean_strings]
    zipped_list = list(zip(merged_list[0], merged_list[1]))
    result_as_list = list(map(list, zipped_list))

    return result_as_list


def export_as_dict(zipped_list):
    """
    This function converts a zipped list into a dictionary
    :param zip_list: in the zipped list, a publication id is concatenated with a fully processed string
    :return: List of dictionaries have the following structure: [{id: 123222 , "data_for_wordcloud" : "Lorem, ipsum, dolor, sit, amet"},{...} ]
    """
    result_list = []

    for count in range(len(zipped_list)):
        result_list.append({"id": int(zipped_list[count][0]), "data_for_wordcloud": zipped_list[count][1]})

    return result_list


def preprocess_data_for_wordcloud(collection_name):
    """
    In this function, the pipeline is completely controlled and the individual steps are executed one after the other
    :param collection_name: Name of the collection in which the items should be stored
    """
    # Import publication Data
    print("Processing of wordcloud data has started...")

    columns = ['id', 'title_nlp', 'keywords_nlp', 'abstract_nlp', 'publYear']
    raw_data = get_wi_publication_data_df(columns)
    print("Data Import is completed")

    string_per_publication = build_sting_per_publication(raw_data)
    print("The creation of the String for each publication is complete")

    clean_data = clean_string(string_per_publication)
    dictionary_for_export = export_as_dict(clean_data)
    print("Data processing is complete")
    # print(dictionary_for_export)
    print("Load data to Database: ")
    # The third parameter specifies which collection may be deleted for writing with new data (security mechanism)
    complete_push_to_mongo_data_lake(collection_name, dictionary_for_export, collection_name)
    print(" ")
    print("Execution was a success!")


if __name__ == "__main__":
    # Run the pipeline
    preprocess_data_for_wordcloud('publication_wordcloud_data')
