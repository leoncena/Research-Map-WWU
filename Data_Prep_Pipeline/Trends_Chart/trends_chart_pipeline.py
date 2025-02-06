"""
This script uses top_2_vec to organize data by topic and aggregate it by year of publication so that it can be used to display a line chart
"""

# load Data from Database
import nltk
import pandas as pd
from pipeline_helper import complete_push_to_mongo_web , build_sting_per_publication, get_wi_publication_data_df
from top2vec import Top2Vec

nltk.download('stopwords')
from nltk.corpus import stopwords


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


def generate_artificial_keywords_as_dict(model):
    """
    Create a dictionary in which the 3 best matching keywords are assigned to a list of publ_ids.
    These are filtered to prevent multiple similar words
    format: 1: {'topic_keywords:[algorithms,optimization,speed],
                'documents_with_id': [1235,2353,2345...]
    :param model:
    :return: result_dict
    """

    count = 0
    result_dict = {}

    for actual_id in range(model.topic_sizes.size):
        # Transfer document id of current topic to list
        list_all_documents_actual_id = get_all_document_id_list(model, actual_id)
        actual_document_id_all_int = convert_strings_to_ints(list_all_documents_actual_id)

        # Extract the current heading words and convert to list
        actual_topic_words = get_best_keywords(model, actual_id)

        result_dict[str(count)] = {'topic_words': actual_topic_words[0:3],
                                   'documents_with_id': actual_document_id_all_int}
        count += 1

    return result_dict


# helper functions for export_with_keywords_all_int
def get_all_document_id_list(model, topic_no):
    '''
    Returns all Document_ids that can be assigned to topic_no
    :param model: trained data model
    :param topic_no: topic
    :return: document_ids
    '''

    number_of_publications = get_topic_sizes_by_id(model, topic_no)
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


def convert_strings_to_ints(lst):
    return list(map(int, lst))


def get_best_keywords(model, actual_topic_no):
    """
    The topic words of a topic are loaded and the individual words are filtered to determine whether
    they are stop words or are very similarly related, such as model and models.
    If they are then cleaned, the first 4 are returned
    :param model: trained data model
    :param actual_topic_no: id of the currently viewed heading
    :return: return of the 4 keywords that have the highest fit
    """
    topic_words, word_scores, topic_nums = model.get_topics()
    # determine the number of keywords which is selected per article

    # Delete remaining stopwords and similar keywords from the keyword list
    cleaned_keyword_data = clean_artificial_keywods(list(topic_words[actual_topic_no]))

    # Protection in case too many keywords are deleted by the clean_artificial_keywords
    if len(cleaned_keyword_data) < 3:
        string_data = cleaned_keyword_data[0:len(cleaned_keyword_data)]
    else:
        string_data = cleaned_keyword_data[0:3]

    keyword_list = []
    for actual_keyword in list(string_data):
        keyword_list.append(actual_keyword)
    return keyword_list


# clean keyword data
def clean_artificial_keywods(keyword_list):
    """
    In this function, the data for the selection of the artificial_keywords is cleaned by first removing stopwords and then similar words
    :param keyword_list: list with keywords from Top2Vec
    :return: string with cleaned keywords
    """
    # Delete stop words
    keywords_without_stopwords = preprocess_data_delete_stopwords(keyword_list)
    # Delete similar words
    keywords_clean = compute_keyword_list_without_simular_words(keywords_without_stopwords)

    return keywords_clean


# Filter out stop words with NLP
def preprocess_data_delete_stopwords(keyword_list):
    """
    Function that filters out the strings that are stopwords from a list of strings
    :param keyword_list: List containing keywords
    :return: keywords_without_stopwords
    """
    keywords_without_stopwords = []
    # Remove stopwords from Top2Vec result
    for actual_keyword in keyword_list:
        is_stopword = check_is_no_stopword(actual_keyword)

        if (is_stopword == True):
            keywords_without_stopwords.append(actual_keyword)
    return keywords_without_stopwords


def check_is_no_stopword(word):
    """
    Check if a word is a stop word
    :param word: a single word as a string
    :return: truthful whether stopword
    """
    stop_words = set(stopwords.words("english"))
    if word.lower() not in stop_words:
        return True
    else:
        return False


def compute_keyword_list_without_simular_words(clean_keyword_list):
    """
    In this function, a list is created containing only dissimilar keywords
    :param clean_keyword_list: List of keywords in which there are no more stop words
    :return: List of dissimilar keywords
    """
    list_without_simular_keywords = []
    # Check if something similar is already in the list, then don't add it anymore
    for actual_keyword in clean_keyword_list:
        # Filter out all keywords with a length < 3, otherwise the similarity measure cannot be calculated
        if len(actual_keyword) <= 3:
            continue
        # If there is no keyword yet --> add it
        if len(list_without_simular_keywords) == 0:
            list_without_simular_keywords.append(actual_keyword)
        else:
            # Check if a similar word already exists in list_without_simular_keywords
            can_be_added = compute_simul_in_list(list_without_simular_keywords,
                                                 actual_keyword)

            if can_be_added == True:
                list_without_simular_keywords.append(actual_keyword)

    return list_without_simular_keywords


def compute_simul_in_list(list_without_simular, keyword_to_compare):
    """
    With this function all trigrams should be calculated from the list_without_simular_keywords and then also a trigram from the word to be checked
    If there is a similar word, false is returned, otherwise true
    :param list_without_simular_keyword: List in the no similar and no stop words are included
    :param keyword_to_compare: Keyword that is compared to the existing words
    :return: token
    """

    # Create n_gram of word what to do
    n_gram_word_to_compare = ngram(keyword_to_compare, 3)

    # Specifies whether to continue, if false, then abort
    token = True
    # Creating the trigrams of the list_without_simular
    for actual_word in list_without_simular:
        actual_n_gram = ngram(actual_word, 3)
        # Calculate similarity of the data
        similarity_result = jaccard(n_gram_word_to_compare, actual_n_gram)
        # If similarity is high then loop aborts, element is discarded
        if similarity_result >= 0.5:
            token = False
            break
    return token


def jaccard(ngram_A, ngram_B):
    """
    Compares the similarity of two trigrams using Jaccard's coefficient
    :param ngram_A: parsed word in ngram
    :param ngram_B: parsed word in ngram
    :return: result of the Jaccard coefficient
    """
    cut = 0
    for a in ngram_A:
        if a in ngram_B:
            cut += 1
    unification = len(ngram_A) + len(ngram_B) - cut
    return float(cut) / float(unification)


def ngram(string, n):
    """
    Function splits a word into the number of trigrams specified with n
    :param string: String to be parsed
    :param n: Number of letters per part
    :return: List of words broken down into ngrams
    """
    list_of_ngrams = []
    if n < len(string):
        for part in range(len(string) - n + 1):
            tg = string[part:part + n]
            list_of_ngrams.append(tg)
    return list_of_ngrams


# Functions to extract and aggregate trends
def format_data_for_trends_chart(top2vec_result, publ_years_as_dictionary):
    """
    Fusion of attribution of the publication and the year in which it was published.
    Calculate and format data for trends
    Example of dictionary_with_year : [{'year': '1973', 'keywords': {'security, policy, privacy': {'count': 1, 'article_id': [21395569]}}},
                            {'year': '1981', 'keywords': {'multiobjective, pareto, emoa': {'count': 1, 'article_id': [16995309]}}}]
    :param top2vec_result:
    :param publ_years_as_dictionary:
    :return: dictionary_with_year as a list of dictionaries
    """
    # Assigning years to publications
    dataframe_with_topic_per_year = map_topics(top2vec_result, publ_years_as_dictionary)

    # Assigning years to publications
    aggregated_data = aggregate_by_year(dataframe_with_topic_per_year)

    # Create a dictionary for export in the appropriate format
    dictionary_data = convert_df_to_dict(aggregated_data)

    # print(dictionary_data)
    # Format data for export
    dictionary_for_export = format_to_final_form(dictionary_data)

    return dictionary_for_export


def map_topics(data, publ_years_as_dictionary):
    """
    Adding the data is done in three lists which are then converted to pandas series and added!

    :param data: Result from the top2vec algorithm which assigns topics to the individual document IDs
    :param publ_years_as_dictionary: Dictionary of publication dates for each publication
    :return: result_df
    """

    id_list = []
    topic_list = []
    year_list = []
    for topic, topic_data in data.items():
        for document_id in topic_data['documents_with_id']:

            id_list.append(document_id)
            # topic_list.append(tuple(topic_data['topic_words']))
            topic_list.append(", ".join(topic_data['topic_words']))
            # find dates for current id
            year = get_year(publ_years_as_dictionary, str(document_id))
            if year:
                year_list.append(year)
            else:
                year_list.append('nan')

    # Convert List to Series and then turn it into a pandas df
    id_series = pd.Series(id_list)
    topic_series = pd.Series(topic_list)
    year_series = pd.Series(year_list)

    result_df = create_df(topic_series, year_series, id_series)
    return result_df


def create_df(series1, series2, series3):
    """
    This function creates a dataframe from two series in which the topic words are specified with the publication date for each document id
    :param series1:
    :param series2:
    :param series3:
    :return: merged dataframe
    """
    df = pd.concat([series1, series2, series3], axis=1)
    df.columns = ['topic_words', 'publYear', 'id']
    return df


def get_year(doc_dict, doc_id):
    """
    This function returns the year of a publication from a dictionary
    :param doc_dict: dictionary with all publications
    :param doc_id: id of the current document
    :return: publication date
    """
    for _, info in doc_dict.items():
        if info['id'] == doc_id:
            return info['publYear']
    return None


# Neu Funktion die dan entsprechedn Aggregierten
def aggregate_by_year(df):
    """
    This function groups the individual keywords by year and returns a corresponding aggregated data set
    :param df: df has these columns['topic_words', 'publYear', 'id']
    :return: aggregated_dataframe
    """
    grouped = df.groupby(['publYear', 'topic_words'])
    result = grouped['id'].apply(list)
    result = pd.DataFrame(
        {'publYear': result.index.get_level_values(0), 'topic_words': result.index.get_level_values(1),
         'id_list': result.values, 'count': grouped.size().values})
    return result


def convert_df_to_dict(df):
    """
    Aggregated df (data frame) is converted to Dictionary for better exporting
    A list with the following format is returned:{'games, fun, good': {'count': 2, 'article_id': [60159145, 60004879]}, ... }
    :param df:
    :return: pre_formatted_data
    """
    result = {}
    for index, row in df.iterrows():
        year = str(row['publYear'])
        topic = row['topic_words']
        count = row['count']
        ids = row['id_list']
        if year not in result:
            result[year] = {}
        result[year][topic] = {'count': count, 'article_id': ids}
    return result


def format_to_final_form(data):
    """
    This function turns a given data frame into a corresponding dictionary in the form required for the export
    aggregated Df with keyword and year numbers
    :param data: dict of form {'1999': {'lorem, ipsom, dolem': 1}, ...}
    :return:
    """

    new_format_set = []

    # year is key of dict, keywords is value
    for key, value in data.items():
        new_format_set.append({"year": key, "keywords": value})

    return new_format_set


# This function is no longer needed, but don't delete it yet, I have to check it again, Or maybe not?

def df_to_dict(publication_data):
    """
    This function turns a given data frame into a corresponding dictionary in the form required for the export
    :param publication_data: dataframe with publication Data
    :return:
    """
    df = publication_data[['id', 'publYear']]
    result_dict = {}
    for index, row in df.iterrows():
        result_dict[index + 1] = {'id': row['id'], 'publYear': row['publYear']}
    return result_dict


def add_default_values(dictionary_for_export, top2vec_result, publ_years_as_dictionary):
    """
    Add zero values in the trend chart. The input format is
    [{'year': '1973', 'keywords': {
        'government, citizens, divide': {'count': 1, 'article_id': [21395569]}}]

    The output is:
    [{'year': '1973', 'keywords': {
        'government, citizens, divide': {'count': 1, 'article_id': [21395569]},
        'code, test, java': {'count': 0, 'article_id': []}, ...
    ]
    In order to make the trend chart reasonable, the various data must be displayed appropriately
    :param dictionary_for_export: formatted dictionary with no null values added yet
    :param top2vec_result: results from top2vec algorithm
    :param publ_years_as_dictionary: dictionary in which a publication_id is assigned to the year of publication
    :return:dictionary_with_zeros
    """

    list_with_all_topics = map_topics(top2vec_result, publ_years_as_dictionary)

    result = list_with_all_topics['topic_words'].drop_duplicates().values

    # Get all kinds of headlines
    all_topic_as_list = result.tolist()

    # Enrich the dictionary with the zero rows
    dictionary_with_zeros = update_json(dictionary_for_export, all_topic_as_list)

    return dictionary_with_zeros


def update_json(json_data, keyword_list):
    """
    This function adds a zero line to the JSON in places where no publication has appeared for the given theme
    :param json_data:
    :param keyword_list:
    :return: json_data
    """
    for keyword in keyword_list:
        for item in json_data:
            if keyword not in item["keywords"]:
                item["keywords"][keyword] = {"count": 0, "article_id": []}
    return json_data


def create_trends_data(collection_name):
    """
    This function controls the complete pipeline to build the data for the trend chart. The data that is placed on the DB is accessed directly from the frontend.
    Without further processing steps being carried out on the front end. The flow of the pipeline is recorded in a log file,
    which has the name log_trend_charts_pipeline.log.
    :return: null
    """
    # configure logging

    # load publication Data from MongoDB
    print("Load publication Data from Database")
    columns = ['id', 'title_nlp', 'keywords_nlp', 'abstract_nlp', 'publYear']
    publication_data = get_wi_publication_data_df(columns)

    # preprocess titel,abstract,keywords per publication
    print("Preprocess publication Data")
    string_per_publication = build_sting_per_publication(publication_data)

    # create model from data
    print("Create Model:")
    model = build_model(string_per_publication)
    print("Model was created successfully")
    # find artificial keywords with top2vec model
    print("Extract keywords for every ID")
    top2vec_result = generate_artificial_keywords_as_dict(model)

    publ_years_as_dictionary = df_to_dict(publication_data)
    print("Format Data for export")
    # fill the dictionary with frequency of topic trends per year
    filled_dictionary = format_data_for_trends_chart(top2vec_result, publ_years_as_dictionary)

    # Add null values to dictionary
    dictionary_for_export = add_default_values(filled_dictionary, top2vec_result, publ_years_as_dictionary)

    # Store dataframe in Mongo DB
    print("Load data to Database: ")
    # The third parameter specifies which collection may be deleted for writing with new data (security mechanism)
    complete_push_to_mongo_web(collection_name, dictionary_for_export, collection_name)
    print("Execution was a success!")


if __name__ == "__main__":
    # Launch pipeline to create trend
    create_trends_data(collection_name='data_for_trends_with_id')
