"""
Standardize dataframe and process texts so that there is no "noise".
- HTML tags
- Transfer HMTL special characters e.g. umlauts correctly
- Keywords as a list uniform
"""
import pandas as pd
import numpy as np
import re
import ast
import html


def remove_html_tags(text):
    """
    This function removes the HTML-Tags with Regular expressions from a text.
    :text: input text with HTML-Tags
    :return: returns text without HTML, if not NoneType
    """
    clean = re.compile('<.*?>')
    result = re.sub(clean, '', text)
    result = result.replace("\r", "").replace("\n", "")
    # check if the result exists and has a length greater than 1
    if result and len(result) > 1:
        return result
    # else return None

def cleanTextList(df_text):
    """
    This function cleans the column "abstract" and "title". It removes HTML-Tags & processes HTML Unicode.
    :df_text: input column of the dataframe (title or abstract)
    :return: list of clean texts
    """
    rows_without_html = []
    for row in df_text:
        # types in column are either Nan, NoneType or string
        if type(row) is not str:
            rows_without_html.append(None)
        else:
            result = remove_html_tags(str(row))
            if result is not None:
                result = html.unescape(result)
            rows_without_html.append(result)
    return rows_without_html

def cleanKeywordsList(df_keywords):
    """
    This function cleans the column "keywords". It recognizes a list, and other Separators (";",",").
    It processes HTML Unicode.
    :df_keywords: input column of the dataframe "keywords"
    :return: list of lists of keywords
    """
    cleaned_list = []
    reg_list = re.compile("\[.*?\]")

    for row in df_keywords:
        if row is None or type(row) is float or len(row) <= 1:
            cleaned_list.append(None)
        else:    
            if type(row) is list or reg_list.match(str(row)):
                result = ast.literal_eval(str(row))
            else:
                if ";" in row:
                    result = [x.strip() for x in row.split(';')]
                else:
                    result = [x.strip() for x in row.split(',')]
            result = [x.lower() for x in result]
            cleaned_list.append(html.unescape(result))
    return cleaned_list

def clean_dois(df_dois):
    """
    This function extracts all the doi by searching for the doi pattern 10.XXXX/abc
    :df_dois: input column of the dataframe "doi"
    :return: list of dois
    """
    dois = []
    for text in df_dois:
        if type(text) == str:
            match = re.search(r'10\.[0-9]+\/[a-zA-Z0-9\.\-\_]+', text)
            if match:
                dois.append(match.group())
            else:
                dois.append(None)
        else:
            dois.append(None)
    return dois


def preprocessing_cleaning_text(dataframe):
    """
    This function combines alle processsteps for the preprocessing of the column "title", "abstract", "keywords".
    :dataframe: dataframe from the database
    :return: clean dataframe
    """
    df_new = dataframe.copy()
    df_new["cfTitle"] = cleanTextList(dataframe["cfTitle"])
    df_new["cfAbstr"] = cleanTextList(dataframe["cfAbstr"])
    df_new["keywords"] = cleanKeywordsList(dataframe["keywords"])
    df_new["doi"] = clean_dois(dataframe["doi"])

    return df_new
