import os
# imports
import re
import time

import numpy as np
import pandas as pd
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
from pybliometrics.scopus import utils as scopus_utils

# SCOPUS API KEYS
scopus_keys = [
    os.getenv('SCOPUS_KEY_1', "ec82f7450fd95aa75a42fe46b1fd16d8"),
    os.getenv('SCOPUS_KEY_2', "e508a9c9edbd69d0a5302c6c8e8ee263"),
    os.getenv('SCOPUS_KEY_3', "653d51124d726f34f65f7c8a13e64aa0")
]
scopus_utils.create_config(scopus_keys)


# Utils
# Cleaning authors


def unify_author_notation(authors):
    """
    Unify the notation of the authors
    i.e. 'Gieseke, F.' -> 'Gieseke F'
    :param authors: String of authors
    :return: Preprocesed string of authors with unified notation
    """

    pattern = r',(?! )'  # match comma not followed by space
    regex = re.compile(pattern)
    authors = regex.sub(', ', authors)  # adds space after comma if regex matches

    if ";" in str(authors):
        # remove comma separating surname and firstname
        authors = authors.replace(".", "")
        authors = authors.replace(",", "")
        authors = authors.replace(";", ",")

    # while string ends with a comma or a dot, remove it
    while str(authors).endswith(',') or str(authors).endswith('.'):
        authors = authors[:-1]

    return authors


# parse authors
def parse_authors_from_mongo(authors):
    """
    Parses authors from db to a list of author surnames since they are always present
    e.g. "Becker J, Niehaves B" -> ["Becker", "Niehaves"]
    :param authors: Authors entry in the syntax: "Surname1 Firstname1(1 letter or complete), Surname2 Firstname2(1 letter or complete), ..."
    :return: List of author surnames
    """
    authors = unify_author_notation(authors)
    author_list = []
    author_counter = 0
    for author in str(authors).split(","):
        author_counter += 1
        author_list.append(author.strip().split(" ")[0])
        # brak for loop if more than 8 authors (scopus does not show all sometimes)
        if author_counter > 8:
            break
    # remove empty strings in author_list (happen when there is a comma at the end)
    author_list = list(filter(None, author_list))

    # remove entries that are only one letter long
    author_list = [author for author in author_list if len(author) > 1]

    return author_list


# Levenshtein distance for selecting matches
def levenshtein_distance(token1, token2):
    """
    Levenshtein distance is a string metric for measuring the difference between two sequences. \n
    Informally, the Levenshtein distance between two words is the minimum number of \n
    single-character edits (insertions, deletions or substitutions) \n
    required to change one word into the other.
    Source: https://blog.paperspace.com/implementing-levenshtein-distance-word-autocomplete-autocorrect/
    :param token1: First token to compare with
    :param token2: Sceond token to compare with
    :return: Levenshtein distance of two tokens
    """
    distances = np.zeros((len(token1) + 1, len(token2) + 1))

    for t1 in range(len(token1) + 1):
        distances[t1][0] = t1

    for t2 in range(len(token2) + 1):
        distances[0][t2] = t2

    a = 0
    b = 0
    c = 0

    for t1 in range(1, len(token1) + 1):
        for t2 in range(1, len(token2) + 1):
            if token1[t1 - 1] == token2[t2 - 1]:
                distances[t1][t2] = distances[t1 - 1][t2 - 1]
            else:
                a = distances[t1][t2 - 1]
                b = distances[t1 - 1][t2]
                c = distances[t1 - 1][t2 - 1]

                if a <= b and a <= c:
                    distances[t1][t2] = a + 1
                elif b <= a and b <= c:
                    distances[t1][t2] = b + 1
                else:
                    distances[t1][t2] = c + 1

    return distances[len(token1)][len(token2)]


def choose_publication_with_min_distance(token_reference_title, publication_list):
    """
    Chooses the Publication from a list of tokens with the minimum levenshtein distance to the given token


    :param token_reference_title: Reference token to compare to (title of the query publication)
    :param publication_list: List of publication to take their title for comparison, type pybliometrics Document
    :return: Element from tokenList with minimum levenshtein distance to token
    """
    min_distance = 1000000000000  # guardian, should be enough
    min_distance_publication = None
    for publication_document in publication_list:
        current_token = publication_document.title
        distance = levenshtein_distance(token_reference_title, current_token)
        if distance < min_distance:
            min_distance = distance
            min_distance_publication = publication_document
    return min_distance_publication


# Query Construction

def scopus_chain_with_and(queries):
    """
    Chains scopus queries with AND
    :param queries: list of Scopus queries to chain
    :return: chained scopus query
    """
    query_chained = ' AND '.join(queries)
    # append braces around the query
    return f'({query_chained})'


def scopus_title_query(title):
    """
    Constructs a scopus query for the title of a paper
    :param title: Title of a paper to search for in scopus
    :return: Scopus query
    """
    # check if title starts and ends with quotes, if so remove them
    # e.g. "Lorem ipsum paper" -> Lorem ipsum paper
    if str(title).startswith('"') and str(title).endswith('"'):
        print('Title starts and ends with quotes, removing them')
        title = title[1:-1]
    # count how many quotes are in the title
    quotes = title.count('"')
    # if there are an odd number of quotes, remove the last found quote character
    # find position of last quote
    # e.g. "Lorem "ipsum paper" -> "Lorem ipsum "paper"
    if quotes % 2 != 0:
        print('Title contains an odd number of quotes, removing the last one')
        last_quote = title.rfind('"')
        title = title[:last_quote] + title[last_quote + 1:]

    return f'TITLE ("{title}")'


def scopus_author_query(author_surname):
    """
    Constructs a scopus query a author \n
    Uses surname since they are always written fully out
    :param author_surname: Surname of a author
    :return: Scopus query for that author
    """
    return f'AUTHOR-NAME ({author_surname})'


def scopus_authors_queries_from_string(authors_string):
    """
    Creates a chained scopus query for the authors of a paper \n
    Only using the processed surnames of the author
    :param authors_string: Unprocessed string ot the authors of a paper from db
    :return: Scopus query incoprporating the authors
    """
    # preprocessing (unify notation and parse to list)
    authors_list = parse_authors_from_mongo(authors_string)
    queries = []
    for author in authors_list:
        queries.append(scopus_author_query(author))
    return scopus_chain_with_and(queries)


def scopus_flk_query(title, authors_string):
    """
    Creates a scopus query for a paper according Research Map syntax (see above) \n
    Using title and surnames of authors
    :param title: Title of the paper from db
    :param authors_string: Unprocessed string ot the authors of a paper from db
    :return: Scopus query for the paper
    """
    queries = []
    queries.append(scopus_title_query(title))
    queries.append(scopus_authors_queries_from_string(authors_string))
    return scopus_chain_with_and(queries)


# Retrieving the information - Inner methods

def fire_scopus_publication_query(query):
    """
    Fires a query to the scopus API and returns the results \n
    Needs processed query string as input
    Needs config file with API key
    :param query: processed query string
    :return: Tuple List with scopus reesults of type pybliometrics.scopus.scopus_search contaiing concrete results.ScopusSearch and log message
    """
    log = ''
    if query is None:
        log = 'Query is None'
        return None, log
    else:
        try:
            scopus_results = ScopusSearch(query, refresh=True)
            scopus_results
            log = f"Scopus query successful: {query}"
            return scopus_results, log
        except Exception as e:
            print(f"Error while querying scopus with query: {query} - error: {e}")
            log = f'Error scopus -  query: {query}, error: {e}'
            return None, log


def parse_scopus_query_result(scopus_result, publication_title_db):
    """
    Method takes the rsult of the scopus search and parses it \n
    Outputs the most similar publication of the result or handles Nones
    If there are more than one results, the best fit is calculated by the Levenshtein distance of the title
    :param publication_title_db: Title of the publication in the database
    :param scopus_result: Returned object from ScopusSearch
    :return: Dict with parsed scopus result or None
    """
    result_publication = None
    log = None
    if scopus_result is None:
        log = '[parse_scopus_query_result] Passed scopus_result is None'
        return result_publication, log

    # amount of publications found
    amount_results = scopus_result.get_results_size()
    publications_results = scopus_result.results

    # logic for handling the results
    # case 1: no results
    if amount_results == 0:
        msg = '[parse_scopus_query_result] No results found for valid query'
        print(f'\033[91m {msg} \033[0m')
        log = msg
        return result_publication, log
    # case 2: one result (good)
    if amount_results == 1:
        msg = '[parse_scopus_query_result] One result found for valid query'
        print(f'\033[92m {msg} \033[0m')
        log = msg
        result_publication = publications_results[0]
        return result_publication, log
    # case 3: more than one result (tricky, need levensthein distance)
    if amount_results > 1:
        # choose with Levenshtein distance
        result_publication = choose_publication_with_min_distance(publication_title_db, publications_results)
        msg = '[parse_scopus_query_result] More than one result found for valid query, choose with Levenshtein distance'
        # compare reference_title with result_title
        msg2 = f'> Query from DB:\n\t"{publication_title_db}",\n > Result from Scopus:\n\t"{result_publication.title}"'
        print(f'\033[93m {msg} \033[0m')
        print(f'\033[93m {msg2} \033[0m')
        log = msg
        return result_publication, log


def parse_scopus_publication_document(scopus_document):
    """
    Parses a scopus document into a dict with the relevant information
    :param scopus_document: Scopus document from scopus search
    :return: Dict with relevant information, ready to use
    """
    if scopus_document is None:
        print(f'\033[91m [parse_scopus_publication_document] Passed scopus_document is None \033[0m')
        return None, {'error': 'passed scopus_document is None'}
    final_information = {}
    # get information from scopus document
    # title
    try:
        final_information['title'] = scopus_document.title
    except Exception as e:
        print(f'Error while parsing title: {e}, probably None')
        final_information['title'] = None
    # author_names, form of "Lastname, Firstname; Lastname, Firstname; ..."
    try:
        final_information['authors'] = scopus_document.author_names
    except Exception as e:
        print(f'Error while parsing authors: {e}, probably None')
        final_information['authors'] = None
    # doi
    try:
        final_information['doi'] = scopus_document.doi
    except Exception as e:
        print(f'Error while parsing doi: {e}, probably None')
        final_information['doi'] = None
    # eid (elsevier id, important for abstract retrieval)
    try:
        final_information['eid'] = scopus_document.eid
    except Exception as e:
        print(f'Error while parsing eid: {e}, probably None')
        final_information['eid'] = None
    # keywords need to be parse because they are a string
    # separated by ' | '
    try:
        raw_keywords = scopus_document.authkeywords
        final_information['keywords'] = raw_keywords.split(' | ')
        # strip whitespaces
        final_information['keywords'] = [keyword.strip() for keyword in final_information['keywords']]
    except Exception as e:
        print(f'Error while parsing keywords: {e}, probably None')
        final_information['keywords'] = None

    # abstract
    # abstracts are not always part of the scopus document
    # need to retrieve them with the eid/doi in a separate request if they are not part of the document

    # check if abstract is part of the document
    final_abstract = None
    try:
        abstract_document = scopus_document.description
    except Exception as e:
        print(f'Error while parsing abstract: {e}, probably not included in document')
        abstract_document = None
    if abstract_document is not None:
        final_abstract = abstract_document
        print(f'Found abstract in document')

    # only of abstract not found in document, try to retrieve it with eid
    if final_abstract is None:
        # if abstract is not part of the document, retrieve it with the eid or doi from scopus
        # identifier is either eid or doi if available
        if final_information.get('eid') is not None:
            identifier = final_information.get('eid')
        elif final_information.get('doi') is not None:
            identifier = final_information.get('doi')
        else:
            identifier = None

        # if identifier is not None, retrieve abstract
        if identifier is not None:
            try:
                abstract_object = AbstractRetrieval(identifier)
            except:
                print(f'Error while retrieving abstract with identifier: {identifier}')
                abstract_object = None

        # parse abstract, the real abstract is either in the abstract attribute or description attribute
        if abstract_object is not None:
            # check if abstract is in abstract attribute
            try:
                abstract_object_abstract_attribute = abstract_object.abstract
            except:
                print(f'Error while parsing abstract from abstract attribute')
                abstract = None
            # check if abstract is in description attribute
            try:
                abstract_object_description_attribute = abstract_object.description
            except:
                print(f'Error while parsing abstract from description attribute')
                abstract = None

            # if abstract is in abstract attribute, use it
            if abstract_object_abstract_attribute is not None:
                final_abstract = abstract_object_abstract_attribute
                print(f'Found abstract in abstract attribute via eid/doi')
            elif abstract_object_description_attribute is not None:
                final_abstract = abstract_object_description_attribute
                print(f'Found abstract in description attribute via eid/doi')

            # if not found until now there is no abstract and it remains None

    final_information['abstract'] = final_abstract

    # data source flag (legal reasons)
    final_information['data_source'] = 'scopus-api'

    # logging
    # look what attributes we could find that are not none and create a log message
    found_attributes = [key for key, value in final_information.items() if value is not None]
    log_found_attributes = f'Found attributes: {found_attributes}'

    return final_information, log_found_attributes


# Two different search methods

def search_publication_on_scopus_single_with_title_authors(publication_title, publication_authors):
    """
    Method takes title and authors from a publication and searches for it on scopus \n
    Returns the found information and handles the whole process internally \n
    Information is returned as a dict
    :param publication_title: Title of the publication, can come from the database or a df
    :param publication_authors: Authors of the publication, can come from the database or a df
    :return: Dict with relevant information, ready to use and logs
    """
    # first we need to construct the query string for the scopus search
    query = scopus_flk_query(publication_title, publication_authors)
    if query is None:
        return None, {'error': 'query is None'}
    # fire the query
    query_result, query_log = fire_scopus_publication_query(query)
    # parse the result, we receive a scopus document and the log
    result_publication_document, parse_scopus_query_result_log = parse_scopus_query_result(query_result,
                                                                                           publication_title)
    # parse the scopus document into a dict so we can use it
    scopus_publication_information, log_found_attributes = parse_scopus_publication_document(
        result_publication_document)

    # collect and aggregate all logs as descriptive dict
    log_collection = {'log_title': publication_title,
                      'used_title': publication_title,
                      'used_authors': publication_authors,
                      'query': query,
                      'query_type': 'Title-Author-Search',
                      'query_log': query_log,
                      # log from parsing the query result, e.g. choosing the right publication
                      'parse_scopus_query_result_log': parse_scopus_query_result_log,
                      'log_found_attributes': log_found_attributes}

    return scopus_publication_information, log_collection


def search_publication_on_scopus_single_with_doi(doi, publication_title):
    """
    Method takes DOI and searches for it on scopus \n
    Returns the found information and handles the whole process internally \n
    Similar to method: search_publication_on_scopus_single_with_title_authors
    :param publication_title: Title of the publication
    :param doi: DOI number
    :return: Dict with relevant information, ready to use and logs
    """

    # first consutruct the query string for the scopus search

    # DOI(10.1109/DLRP.2000.942152)
    query = f'DOI({doi})'
    # fire the query
    query_result, query_log = fire_scopus_publication_query(query)
    # parse results (should only be 1 or 0 since DOI is exclusive)
    result_publication_document, parse_scopus_query_result_log = parse_scopus_query_result(query_result,
                                                                                           publication_title)

    # parse the document into a dict so we can use it
    scopus_publication_information, log_found_attributes = parse_scopus_publication_document(
        result_publication_document)

    # collect and aggregate all logs as descriptive dict
    log_collection = {'log_title': publication_title,
                      'used_title': publication_title,
                      'query': query,
                      'query_type': 'DOI-Search',
                      'query_log': query_log,
                      # log from parsing the query result, e.g. choosing the right publication
                      'parse_scopus_query_result_log': parse_scopus_query_result_log,
                      'log_found_attributes': log_found_attributes}

    return scopus_publication_information, log_collection


# search wrapper combining both methods

def search_single_publication_on_scopus_final(publication_id, publication_title, publication_authors, doi=None):
    """
    Method combines DOI search with title-author search. Check what is available and use the best available method
    :param publication_id: ID of the publication in cris
    :param publication_title: Title of the publication
    :param publication_authors: Authors of the publication from cris
    :param doi: DOi of publication
    :return: Dict with relevant information, ready to use; log_collection
    """
    doi_results = None
    title_author_results = None

    # time measuere of doi check
    start_time = time.time()
    # checl if doi is not NOne and notna

    if doi is not None and pd.notna(doi):
        print(f'Checking DOI: {doi}')
        # if doi is not None, search for publication on scopus with doi
        scopus_publication_information_doi, log_collection_doi = search_publication_on_scopus_single_with_doi(doi,
                                                                                                              publication_title)
        doi_results = [scopus_publication_information_doi, log_collection_doi]
        # if works, return the results otherweise continue with title-author search
        if scopus_publication_information_doi is not None:
            msg = f'Found publication via DOI search for publication id: {publication_id}'
            # print blue text
            print(f'\033[94m {msg} \033[0m')
            print(f'DOI check took {round(time.time() - start_time, 4)} seconds')
            return doi_results
    end_time = time.time()
    print(f'DOI check took {round(end_time - start_time, 4)} seconds')

    # if doi search without sucess we try classic search, we dont reach that line if sucess because return statement
    print(f'No DOI found for publication: {publication_id}, searching with title and authors')

    # time measuere of title-author check
    start_time = time.time()
    scopus_publication_information_title_author, log_collection_title_author = search_publication_on_scopus_single_with_title_authors(
        publication_title=publication_title, publication_authors=publication_authors)
    title_author_results = [scopus_publication_information_title_author, log_collection_title_author]
    end_time = time.time()
    print(f'Title-Author check took {end_time - start_time} seconds')
    return title_author_results


# search wrapper for multiple publications
# not used currently, considering removing
def search_multiple_publications_on_scopus_by_df(publications_df):
    """
    Method takes a df with publications and searches them all on scopus \n
    Determines what kind of search is useful
    :param publications_df: DF with publications (export from mongo db)
    :return: List of dict with results
    """
    final_results = []
    counter = 1
    print(f'--- Start')
    for index, row in publications_df.iterrows():
        # mesaure time of row iteration
        start_row_time = time.time()

        try:
            publication_id = row.get('id')
            publication_title = row.get('cfTitle')
            publication_authors = row.get('srcAuthors')
            publication_doi = row.get('doi')
            print(
                f'Starting search for publication: {publication_id}, {publication_title}, index: {counter} out of {len(publications_df)}')
            row_result = {'id': publication_id, 'scraping_result': None, 'scopus_log': None}

            print(f'Searching for publication {counter} of {len(publications_df)}')
            scopus_publication_result, scopus_log_collection = search_single_publication_on_scopus_final(
                publication_id=publication_id,
                publication_title=publication_title,
                publication_authors=publication_authors,
                doi=publication_doi)
            # check if sucessful
            if scopus_publication_result is not None:
                print(f'Sucessfully found publication {counter} of {len(publications_df)}')

            # add the result to the row
            row_result['scraping_result'] = scopus_publication_result
            row_result['scopus_log'] = scopus_log_collection
            final_results.append(row_result)
            counter += 1


        except Exception as e:
            msg = (
                f'[Scopus_FLK_Wrapper] Error while searching for publication {counter} of {len(publications_df)} with id {publication_id} - error: {e}')
            # print in red
            print('\x1b[6;30;41m' + msg + '\x1b[0m')
            pass

        end_row_time = time.time()
        print(f'Row took {round(end_row_time - start_row_time, 4)} seconds')
        print(f'\n---\n')

    return final_results
