import os

import deepl
import pandas as pd

AUTH_KEY = os.getenv('DEEPL_AUTH_KEY', '81c28c3d-bc41-2178-db4e-f30422da8c20:fx')
TARGET_LANG = 'EN-GB'
translator = deepl.Translator(auth_key=AUTH_KEY)


def translate_publications(df: pd.DataFrame):
    """Translate the publications in the given dataframe using DeepL.
    Args:
        df (pd.DataFrame): Dataframe containing the publications to be translated.
    Returns:
        pd.DataFrame: Dataframe containing the translated publications.
    """

    df['title_nlp'] = ''
    df['abstract_nlp'] = ''
    df['keywords_nlp'] = ''
    df['translated'] = False

    for index, row in df.iterrows():

        if row['lang'] is None or row['lang'] == 'en':
            df.at[index, 'title_nlp'] = row['cfTitle'] if row['cfTitle'] is not None else ""
            df.at[index, 'abstract_nlp'] = row['cfAbstr'] if row['cfAbstr'] is not None else ""
            df.at[index, 'keywords_nlp'] = row['keywords'] if row['keywords'] is not None else ""
            continue
        try:
            df.at[index, 'title_nlp'] = translator.translate_text(row['cfTitle'], target_lang=TARGET_LANG).text if row[
                                                                                                                       'cfTitle'] is not None else ""
            df.at[index, 'abstract_nlp'] = translator.translate_text(row['cfAbstr'], target_lang=TARGET_LANG).text if \
            row['cfAbstr'] is not None else ""

            if isinstance(row['keywords'], list) and row['keywords']:
                df.at[index, 'keywords_nlp'] = [translator.translate_text(keyword, target_lang=TARGET_LANG).text for
                                                keyword in row['keywords']]
            # flag to know that this row was translated
            df.at[index, 'translated'] = True

        except Exception as e:
            df.at[index, 'title_nlp'] = str(row['cfTitle'])
            df.at[index, 'abstract_nlp'] = str(row['cfAbstr'])
            df.at[index, 'keywords_nlp'] = str(row['keywords'])
            print(e)

    return df
