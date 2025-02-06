"""

Consider changing the file name to dat_filler_pipeline.py
- Goal: Fill the data and prepare them for data team (front end data export is not part of this script)


This script should trigger the data filling process for new publications and prepare them for further processing.
Steps:
    1. Determine which publications are new
       - New publications are determined with Δ(publication.id,publication_filled.id)
    2. Retrieve the information for the new publications and save the information in the mongo collection "publications"
    3. Prepare the new publications for further processing (for now add language attribute)
    4. Preprocessing for NLP
        4.1. Cleaning
        4.2. Translating german publications to english (create new columns: title_nlp, abstract_nlp, keywords_nlp
        with translated text)

    # at the end change so only push to mongo after all steps are done and not after each step
"""
import os
import sys

path_1 = os.getenv('PYTHONPATH_ENV', "C:\\Users\\hendr\\IdeaProjects\\ps-research-map\\Data_Prep_Pipeline")
path_2 = os.getenv('PYTHONPATH_ENV_2',
                   "C:\\Users\hendr\\IdeaProjects\\ps-research-map\\Data_Prep_Pipeline\\Research_Scraper")

sys.path.extend([path_1, path_2])

import numpy as np

from Research_Scraper.Research_Scraper_Code import Publication_Filler as Pub_filler
import data_prep_helper
from Research_Scraper.Research_Scraper_Code import utils
from Preprocessing import Preprocessing
from Translator import translator


# Extracted functions
def add_and_extract_language_column(target_collection):
    """
    Extract and unpacks the language from cfLang (nested json) and adds it cleaned as a new column
    """
    wi_df_publication_filled['cfLang_extracted'] = wi_df_publication_filled['cfLang'].apply(
        lambda x: x['cfName'] if x is not None else None)
    # create clean lang attribute
    wi_df_publication_filled['lang'] = np.where(wi_df_publication_filled['cfLang_extracted'] == 'Englisch', 'en',
                                                np.where(wi_df_publication_filled['cfLang_extracted'] == 'Deutsch',
                                                         'de',
                                                         np.where(wi_df_publication_filled['cfLang_extracted'].isna(),
                                                                  None, 'other')))
    # wipe the collection to update whole df
    print(f'[Filling Pipeline] Start wiping to prepare for update')
    utils.wipe_mongo_collection(target_collection)
    print('[Filling Pipeline] Pushing data back to mongo collection "publication_filled" to update the collection.')
    utils.safe_push_to_mongo(df=wi_df_publication_filled, collection_name=target_collection)


# total pipeline
def fire_total_filler_pipeline(target_collection):
    global wi_df_publication_filled  # global to be able to use it in sub functions
    print(f'[Filling Pipeline] Step 1: Determine new publications')
    # 1. Determine which publications are new
    # 1.1. Get the publications from the mongo collection "publication"
    wi_ids_publication = data_prep_helper.get_wi_ids()

    # 1.2. Get the publications from the mongo target collection aka by default, collection "publication_filled"
    wi_df_publication_filled = utils.get_collection_df_from_mongo(collection_name=target_collection)
    wi_ids_publication_filled = wi_df_publication_filled['id'].tolist() if not wi_df_publication_filled.empty else []

    # 1.3. Determine which publications are new
    new_publication_ids = set(wi_ids_publication) - set(wi_ids_publication_filled)

    # convert to list
    new_publication_ids = list(new_publication_ids)

    # handling new publications
    if len(new_publication_ids) > 0:
        print(f'Detected {len(new_publication_ids)} new publications, starting retrieval.')
        # 2. Retrieve the information for the new publications and save the information in the mongo collection "publications"
        print(f'[Filling Pipeline] Step 2: Information Retrieval')
        wi_df_publication_filled, filler_log = Pub_filler.fire_filler_pipeline_on_cris_publications(new_publication_ids,
                                                                                                    write_to_file=False,
                                                                                                    target_collection=target_collection)

        print(f'[Filling Pipeline] Step 3: Preparing, adding language column')
        # 3. Prepare the new publications for further processing (for now add language attribute)
        # 3.1. Get the publications from the mongo collection target collection aka "publication_filled"
        wi_df_publication_filled = utils.get_collection_df_from_mongo(collection_name=target_collection)

        # 3.2. Add lang column to the publications with extracted language
        add_and_extract_language_column(target_collection=target_collection)

        print(f'[Filling Pipeline] Step 4: Preporcessing for NLP')
        # Outline for NLP preprocessing methods, to be inserted here when ready
        # 4. Preprocessing for NLP
        print(f'[Filling Pipeline] Step 4.1: Attribute cleaning')
        # # 4.1. Preprocessing : Cleaning
        wi_df_publication_filled = Preprocessing.preprocessing_cleaning_text(wi_df_publication_filled)
        # # Saving results
        print(f'[Filling Pipeline] Start wiping to prepare for update of preprocessing cleaning')
        utils.wipe_mongo_collection(target_collection)
        print(f'[Filling Pipeline] Pushing data back to mongo collection {target_collection} to update the collection.')
        utils.safe_push_to_mongo(df=wi_df_publication_filled, collection_name=target_collection)

        # preprocessing_cleaning(wi_df_publication_filled)

        print(f'[Filling Pipeline] Step 4.2: DeepL translation')
        # 4.2. Preprocessing : Translating german publications to english (create new columns: title_nlp, abstract_nlp, keywords_nlp
        # with translated text)
        wi_df_publication_filled = translator.translate_publications(wi_df_publication_filled)
        # # Saving results
        print(f'[Filling Pipeline] Start wiping to prepare for update of deepl translations')
        utils.wipe_mongo_collection(target_collection)
        print(f'[Filling Pipeline] Pushing data back to mongo collection {target_collection} to update the '
              f'collection.')
        utils.safe_push_to_mongo(df=wi_df_publication_filled, collection_name=target_collection)

        print('[Filling Pipeline] End of pipeline')

    else:
        print(
            f'[Filling Pipeline] No new publications found. No new publications will be added to the mongo collection {target_collection}.')
        print('[Filling Pipeline] End of pipeline')


if __name__ == '__main__':
    # before using new name of collectiion make sure that the
    # wiping permissions are set correctly in the wipe method
    fire_total_filler_pipeline('publication_filled')
