"""
In this script, with the help of Top2Vec , each document ID is the 3 first i.e. also the strongest topic words from the Top2Vec model.
They then serve as 'artificial keywords' and are displayed in the publication search if no real keywords are available.
"""

# load Data from Database
from pipeline_helper import get_wi_publication_data_df, build_sting_per_publication, complete_push_to_mongo_data_lake
from nltk.corpus import stopwords
from top2vec import Top2Vec


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
    Creating a dictionary that returns best keywords for each Id
    :param model:
    :return: result_dict
    """
    count = 0
    result_dict = {}

    for actual_id in range(model.topic_sizes.size):
        list_all_documents_actual_id = get_all_document_id_list(model, actual_id)
        topic_words_actual_id = get_best_keywords(model, actual_id)

        for document_id in list_all_documents_actual_id:
            result_dict[str(count)] = {'id': int(document_id), 'artificial_keywords': topic_words_actual_id}
            count += 1

    return result_dict


pass


def get_best_keywords(model, actual_topic_no):
    """
    The first 4 keywords per publication that have the highest fit to the headline will be returned
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


pass


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
    pass

def get_topic_sizes_by_id(model, id):
    """
    :param model: trained data model
    :param id: the ID for the entered data
    :return: returns the number of items per topic
    """
    data = model.topic_sizes
    return data[id]
    pass




# clean keyword data
def clean_artificial_keywods(keyword_list):
    """
    In this method, the data for the selection of the artificial_keywords is cleaned by first removing stopwords and then similar words
    :param keyword_list: list with keywords from Top2Vec
    :return: string with cleaned keywords
    """
    # Delete stop words
    keywords_without_stopwords = preprocess_data_delete_stopwords(keyword_list)
    # Delete similar words
    keywords_clean = compute_keyword_list_without_simular_words(keywords_without_stopwords)

    return keywords_clean
    pass


# Filter out stop words with NLP
def preprocess_data_delete_stopwords(keyword_list):
    """
    Function that filters out the strings that are stopwords from a list of strings
    :param keyword_list: List containing keywords
    :return:
    """
    keywords_without_stopwords = []
    # Remove stopwords from Top2Vec result
    for actual_keyword in keyword_list:
        is_stopword = check_is_no_stopword(actual_keyword)

        if (is_stopword == True):
            keywords_without_stopwords.append(actual_keyword)
    return keywords_without_stopwords
    pass


def check_is_no_stopword(word):
    """
    Check if a word is a stop word
    :param word: a single word as a string
    :return:
    """
    stop_words = set(stopwords.words("english"))
    if word.lower() not in stop_words:
        return True
    else:
        return False


def compute_keyword_list_without_simular_words(clean_keyword_list):
    """
    In this function, a list is created containing only dissimilar keywords
    :param clean_keyword_list: List of stopwords is cleaned
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
            can_be_added = compute_simul_in_list(list_without_simular_keywords, actual_keyword)

            if can_be_added == True:
                list_without_simular_keywords.append(actual_keyword)

    return list_without_simular_keywords
    pass


def compute_simul_in_list(list_without_simular, keyword_to_compare):
    """
    With this function all trigrams should be calculated from the list_without_simular_keywords and then also a trigram from the word to be checked
    If there is a similar word, false is returned, otherwise true
    :param list_without_simular:
    :param keyword_to_compare:
    :return:
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
    pass


def jaccard(ngram_A, ngram_B):
    """
    Compares the similarity of two trigrams using Jaccard's coefficient
    :param ngram_A:
    :param ngram_B:
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


def create_artificial_keywords(collection_name):
    """
    This function controls the complete top2vec pipeline
    :return:
    """
    # load publication Data from MongoDB
    print("Load publication Data from Database")
    columns = ['id', 'title_nlp', 'keywords_nlp', 'abstract_nlp', 'publYear']
    publication_data = get_wi_publication_data_df(columns)

    # preprocess titel,abstract,keywords per publication
    print("Preprocess publication Data")
    string_per_publication = build_sting_per_publication(publication_data)

    # create model from data
    print("Create Model: ")
    model = build_model(string_per_publication)
    print("Model was created successfully")

    # find artificial keywords with top2vec model
    print("Extract keywords for every ID")
    dictionary_for_export = generate_artificial_keywords_as_dict(model)

    # Collection Name specified in params

    # Store dataframe in Mongo DB
    print("Load data to Database: ")
    complete_push_to_mongo_data_lake(collection_name, [dictionary_for_export], collection_name)
    print(" ")
    print("Execution was a success!")
    pass


if __name__ == "__main__":
    # Launch top2vec
    create_artificial_keywords(collection_name="artificial_keywords")
