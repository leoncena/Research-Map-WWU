"""
This script is used for the information retrieval from cris
"""

import json
import time

import numpy as np
import pandas as pd

import Research_Scraper_Code.Scopus_FLK_Wrapper as scopus_flk
# import the necessary packages
from Research_Scraper_Code import utils
from Research_Scraper_Code.Research_Scraper import ResearchScraper


# Processing methods for input data
# These methods are used to make sure that the input data is in the correct format
# special reformatting may be done in the specific methods

def preprocess_title(title):
    """
    This method preprocesses the title of the publication
    We remove control characters and lowercase the title
    :param title: the title of the publication
    :return: the preprocessed title
    """
    title_processed = utils.remove_control_characters(title)
    title_processed = title_processed.lower()
    if '? ' in title_processed:
        title_processed = title_processed.replace('?', ' ')
    elif '?' in title_processed:
        title_processed = title_processed.replace('?', '')

    return title_processed


def preprocess_authors(authors):
    """
    This method preprocesses the authors of the publication from cris
    Control characters in the middle are replaced with a semincolon \n
    Control characters at the beginning and end are removed
    :param authors: authors string from cris
    :return: the preprocessed authors
    """
    if utils.find_backslash_r_n_in_middle_of_string(authors):
        authors_processed = authors.replace('\r\n', '; ')
    else:
        authors_processed = utils.remove_control_characters(authors)

    return authors_processed


def preprocess_doi_for_scopus(doi):
    """
    Preprocess the doi for scopus query, i.e. checks if it a link an extracts the doi from the link if necessary
    :param doi: DOI attribute from cris
    :return: Preprocessed DOI
    """
    if doi is not None:
        if utils.check_if_doi_link(doi):
            doi = utils.extract_doi_from_doi_link(doi)


# triggers the retrieval of information for a publication (with scopus or web scraping)
def retrieve_information_for_publication(publication_id, publication_title, publication_authors, doi, url):
    """
    This method retrieves the information for a publication from cris
    It tries to retrieve the information from scopus and if this fails it tries to retrieve the information with scraping
    :param publication_id: Publication ID from cris
    :param publication_title: Publication title from cris
    :param publication_authors: Publication authors from cris
    :param doi: DOI from cris
    :param url: URL from cris
    :return: [result, log]: Dict with result and dict with log in a list
    """
    # preprocessing
    publication_title = preprocess_title(
        publication_title)  # title is preprocessed independently of the retrieval method
    publication_authors = preprocess_authors(
        publication_authors)  # authors are preprocessed independently of the retrieval method
    doi_for_scopus = preprocess_doi_for_scopus(doi)  # scopus may need the doi to be preprocessed
    doi_for_scraping = doi  # no preprocessing necessary for scraping

    tried_scopus = False
    success_scopus = False
    tried_scraping = False
    success_scraping = False

    # First we try to retrieve the information from scopus
    scopus_result, scopus_log = scopus_flk.search_single_publication_on_scopus_final(publication_id, publication_title,
                                                                                     publication_authors,
                                                                                     doi_for_scopus)
    tried_scopus = True
    # check if the scopus result is good to go
    if scopus_result is not None:
        success_scopus = True
        msg = 'Successfully retrieved information from scopus'  # green
        msg2 = 'Attention: Tried scopus'  # yellow
        print('\033[93m' + msg2 + ' \033[0m' + '\033[92m' + msg + '\033[0m')
        return scopus_result, scopus_log

    # if the scopus result is not good to go, we try to retrieve the information from scraping
    research_scraper = ResearchScraper()
    try:
        scraping_result = research_scraper.scrape_publication_by_doi_and_url(doi_for_scraping, url)
    except Exception as e:
        scraping_result = None
        print(e)
    tried_scraping = True
    if scraping_result is not None:
        success_scraping = True
        msg = 'Successfully retrieved information with scraping'  # green
        msg2 = 'Attention: Tried scopus'  # yellow
        print('\033[93m' + msg2 + ' \033[0m' + '\033[92m' + msg + '\033[0m')
        log = {f'log_title': 'Scraping the id {publication_id} was successful'}
        return scraping_result, log

    # if both methods fail, we return None
    if not success_scopus and not success_scraping and tried_scopus and tried_scraping:
        scopus_log['log_title'] = f'Retrieval via scopus and scraping for the id: {publication_id} failed'
        log = scopus_log
        msg = f'Retrieval via scopus and scraping for the id: {publication_id} failed'  # red
        msg2 = 'Attention: Tried scopus'  # yellow
        print('\033[93m' + msg2 + ' \033[0m' + '\033[91m' + msg + '\033[0m')
        return None, log


# method for retrieving information of a df
def retrieve_information_for_publication_df_to_tuple(df):
    """
    This method will retrieve the information for all publications in the df
    Used therefore is the method retrieve_information_for_publication
    :param df: the df with the publications
    :return: tuple with result dict and log dict
    """
    results = {}
    logs = {}
    for index, row in df.iterrows():
        id_index = row['id']
        title = row['cfTitle']
        authors = row['srcAuthors']
        doi = row['doi']
        url = row['cfUri']
        print(f'Starting retrieve_information_for_publication for id: {id_index}, df index: {index}\n')

        # try retrieval for publication
        try:
            result, log = retrieve_information_for_publication(publication_id=id_index,
                                                               publication_title=title,
                                                               publication_authors=authors,
                                                               doi=doi,
                                                               url=url)
        except Exception as e:
            result = None
            print(f'Exception: {e}')
            log = {'error': f'Exception: {e}'}

        print(f'\nFinished retrieve_information_for_publication for id: {id_index}, df index: {index}\n')

        # append log to result
        if result is not None and log is not None:
            result['log'] = log
        # default log when result is None
        elif result is not None:
            result['log'] = {'log': 'No log'}
        # results.append({id_index: result})
        results[id_index] = result
        logs[id_index] = log

    return results, logs


# processing in the background and then retrieving the information from the resulting df
def run_filler_on_publications_to_filler_df(wi_ids=None, write_to_file=False):
    """
    Retrieves the information for publications and parses the results
    Returns the df with the results and the dict with the logs
    Takes ids as optional parameter to select the publications to be retrieved
    Only retrieves the information for publications that are needed in cris (prefiltering)
    Appends a result_flag to show if the retrieval was successful or not
    Fetched necessary information from mongoDB
    Publications can be written to csv and log to json
    :param write_to_file: Flag to enable writing the results to a file (default: False)
    :param wi_ids: List of ids to be retrieved (optional)
    :return: tuple: df with results and dict with logs
    """
    wi_df = utils.get_wi_publication_data_df(wi_ids)
    # wi_df_missing_values when either abstract or keywords are missing
    wi_df_missing_values = wi_df[wi_df['cfAbstr'].isnull() | wi_df['keywords'].isnull()]
    # first 20 rows
    # wi_df_missing_values = wi_df_missing_values.head(20) -> complete
    start_time = time.time()
    wi_df_missing_values_filler_results = retrieve_information_for_publication_df_to_tuple(wi_df_missing_values)
    end_time = time.time()
    print(f'Time {end_time - start_time}')

    # Create df from results dict
    # filter out None values
    wi_df_missing_values_filler_dict = {}
    wi_df_missing_values_filler_dict = wi_df_missing_values_filler_results[0]
    wi_df_missing_values_filler_log = wi_df_missing_values_filler_results[1]

    for key, value in wi_df_missing_values_filler_dict.items():
        if value is None:
            wi_df_missing_values_filler_dict[key] = {'result_flag': False}
        elif wi_df_missing_values_filler_dict[key].get(
                'error') is not None:  # scraping without sucess should not get a result flag
            wi_df_missing_values_filler_dict[key]['result_flag'] = False
        else:
            wi_df_missing_values_filler_dict[key]['result_flag'] = True

    wi_df_missing_values_filler_final_df = pd.DataFrame.from_dict(wi_df_missing_values_filler_dict, orient='index')
    wi_df_missing_values_filler_final_df['id'] = wi_df_missing_values_filler_final_df.index
    # rearange columns so id is first
    cols = wi_df_missing_values_filler_final_df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    wi_df_missing_values_filler_final_df = wi_df_missing_values_filler_final_df[cols]

    if write_to_file:
        # write result df to csv
        timestamp = utils.get_time_stamp()
        wi_df_missing_values_filler_final_df.to_csv(f'Exports/wi_df_missing_values_filler_final_df_{timestamp}.csv',
                                                    index=False)
        # write log as json
        with open(f'Exports/wi_df_missing_values_filler_log_{timestamp}.json', 'w') as fp:
            json.dump(wi_df_missing_values_filler_log, fp, indent=4)

    return wi_df_missing_values_filler_final_df, wi_df_missing_values_filler_log


# fill up wi_df with filler df
def fill_up_publication_df(publication_df, filler_df, write_to_file=False):
    """
    Processes the filler_df and fills up the publication_df with the information from the filler_df
    :param publication_df: Publication df
    :param filler_df: filler df with additional information
    :param write_to_file: Flag to export results to disk
    :return: Merged df with new information
    """
    # copy entered df
    publication_df = publication_df.copy()
    filler_df = filler_df.copy()

    # filler_df.rename(columns={'Unnamed: 0': 'id'}, inplace=True) # index error, should be fixed
    publication_df['id'] = publication_df['id'].astype('str')
    filler_df['id'] = filler_df['id'].astype('str')
    merged_df = publication_df.merge(filler_df, on='id', how='outer', suffixes=('_wi', '_pipeline'))
    # print col names
    # print(merged_df.columns)

    all_potential_cols = ['id',
                          'cfTitle', 'title',
                          'cfUri', 'url',
                          'keywords', 'keywords_wi', 'keywords_pipeline',
                          'doi', 'doi_wi', 'doi_pipeline',
                          'srcAuthors', 'authors',
                          'cfAbstr', 'abstract',
                          'publYear', 'eid', 'data_source', 'log', 'result_flag', 'error', 'error_doi'
                          ]
    # add columns from potential cols if not already in df
    for col in all_potential_cols:
        if col not in merged_df.columns:
            merged_df[col] = None

    merged_df['id'] = merged_df['id'].astype('str')
    # fill up wi_df with filler df values
    # check if we got new results and get them with np.where
    merged_df['doi'] = np.where(merged_df['doi_wi'].isna(), merged_df['doi_pipeline'], merged_df['doi_wi'])
    merged_df['cfUri'] = np.where(merged_df['cfUri'].isna(), merged_df['url'], merged_df['cfUri'])
    merged_df['keywords'] = np.where(merged_df['keywords_wi'].isna(), merged_df['keywords_pipeline'],
                                     merged_df['keywords_wi'])
    merged_df['cfAbstr'] = np.where(merged_df['cfAbstr'].isna(), merged_df['abstract'], merged_df['cfAbstr'])

    # get cols of merged_df
    cols = merged_df.columns

    all_potential_cols = ['id',
                          'cfTitle', 'title',
                          'cfUri', 'url',
                          'keywords', 'keywords_wi', 'keywords_pipeline',
                          'doi', 'doi_wi', 'doi_pipeline',
                          'srcAuthors', 'authors',
                          'cfAbstr', 'abstract',
                          'publYear', 'eid', 'data_source', 'log', 'result_flag', 'error', 'error_doi', 'cfLang'
                          ]

    # check what col from merged_df is not in all_potential_cols, otherwise we get an error reordering the cols
    missing_cols = [col for col in all_potential_cols if col not in cols]
    # create new cols in merged_df with None values

    for col in missing_cols:
        merged_df[col] = None

    # reorder columns
    merged_df = merged_df[['id',
                           'cfTitle', 'title',
                           'cfUri', 'url',
                           'keywords', 'keywords_wi', 'keywords_pipeline',
                           'doi', 'doi_wi', 'doi_pipeline',
                           'srcAuthors', 'authors',
                           'cfAbstr', 'abstract',
                           'publYear', 'eid', 'data_source', 'log', 'result_flag', 'error', 'error_doi', 'cfLang'
                           ]]
    # name the index column to id
    merged_df.rename(columns={'id': 'id'}, inplace=True)
    # drop columns that are not needed anymore: title, url, keywords_wi, keywords_pipeline, doi_wi, doi_pipeline, abstract
    merged_df.drop(columns=['title', 'url', 'keywords_wi', 'keywords_pipeline', 'doi_wi', 'doi_pipeline', 'abstract'],
                   axis=1, inplace=True)

    if write_to_file:
        # write result df to csv
        timestamp = utils.get_time_stamp()
        merged_df.to_csv(f'Exports/wi_df_final_filled_and_merged_{timestamp}.csv', index=False)

    return merged_df


# bundles all functions and offers a high level interface
def fire_filler_pipeline_on_cris_publications(publication_ids, write_to_file, target_collection):
    """
    Takes a list of publication ids. Gets the data from mongo and fills it up with the publication filler pipeline
    Does every step of the pipeline and returns the final df (ready to use) and a corresponding log
    Optionally writes the results to file (result in csv and log in json)
    :param publication_ids: List of publication ids
    :param write_to_file: Flag to export results to disk
    :param target_collection: Mongo collection name where results are saved
    :return: pub_filled_df (result) and filler_log (json)
    """
    if len(publication_ids) == 0:
        print('No publication ids given')
        return None, None

    # get publication df from mongo with the given ids
    publication_df = utils.get_wi_publication_data_df(publication_ids)

    # run the filler method (retrieves information with scopus or web scraping)
    # may write to disk
    filler_df, filler_log = run_filler_on_publications_to_filler_df(publication_ids, write_to_file=write_to_file)

    # fill up the publication df with the information from the filler df
    publication_filled_df = fill_up_publication_df(publication_df, filler_df, write_to_file=write_to_file)
    # print ids of publication_filled_df
    # print(f'publication_filled_df ids: {publication_filled_df["id"].tolist()}')
    # export to mongo
    utils.safe_push_to_mongo(target_collection, publication_filled_df)
    return publication_filled_df, filler_log
