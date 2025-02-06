"""
Module for the concrete IEEE scraper class.
Requires Python 3.9 or higher.
"""

import json
import re

import requests

from Research_Scraper_Code.scraper_types.scraper_abstract import ScraperAbstract


class ScraperIEEE(ScraperAbstract):
    """
    Class for the specific IEEE Scraper
    """

    @property
    def domain(self):
        return 'ieeexplore.ieee.org'

    @property
    def legal_params(self):
        legal_params = {
            'full',
            'main',
            'title',
            'doi',
            'keywords',
            'abstract',
        }
        return legal_params

    def scrape_by_url(self, url, params=None):
        """
        Scrape a publication with a url \n
        You can scrape everything with params=['full']
        You can also choose what you want to scrape with e.g. params=['title']

        :param url: URL of a publication
        :param params: What data do you want to scrape? ([str])
        :return: Dictionary with scraped data
        """

        # call super class
        super(ScraperIEEE, self).scrape_by_url(url, params)

        scrape_result = {'url': url}

        # params logic

        # check if params are legal otherwise raise error
        self.check_params_legal(params)

        if params is None:
            params = ['main']

        if params == ['main']:
            params = ['title', 'doi', 'keywords', 'abstract']

        if params == ['full']:
            params = self.legal_params  # full = all legal params

        # get soup to extract the json data
        # bs = self.get_bs(url)

        # extract the json data
        json_data = self.get_json_data(url)

        # get title
        if 'title' in params:
            scrape_result['title'] = self.get_title(json_data)

        # get doi
        if 'doi' in params:
            scrape_result['doi'] = self.get_doi(json_data)

        # get keywords
        if 'keywords' in params:
            scrape_result['keywords'] = self.get_keywords(json_data)

        # get abstract
        if 'abstract' in params:
            scrape_result['abstract'] = self.get_abstract(json_data)

        # remove None values from result dict
        scrape_result = {key: value for key, value in scrape_result.items() if value is not None}


        return scrape_result

    # Extract the meta data from the json object
    def get_json_data(self, url):
        """
        Extracts the json object with meta data from the page and parses it to a dict.
        :param url: URL of th publication
        :return: Dict with content of the JSON object
        """
        # extract the line of the text containing the json object
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15'}
        try:
            r = requests.get(url, headers=headers)
            print(r.status_code)
            if r.status_code != 200:
                raise Exception('Connection not successful - Status code not 200')
        except Exception as e:
            print('Error: ', e)
            print('Error: ', url)
            return None
        html_text = r.text
        json_data_regex_pattern = re.compile(r'xplGlobal.document.metadata=.*};')
        json_regex_matches = re.findall(json_data_regex_pattern, html_text)

        assert len(json_regex_matches) == 1

        json_string = json_regex_matches[0]
        json_string = json_string.removeprefix('xplGlobal.document.metadata=')  # remove JS prefix, rquires python 3.9

        json_string = json_string.removesuffix(';')  # remove semicolon at the end
        json_parsed = json.loads(json_string)
        assert isinstance(json_parsed, dict)
        return json_parsed

    # Parsing the data

    def get_doi(self, json_data):
        """
        Extract the DOI from the JSON data
        :param json_data: JSON object with meta data
        :return: DOI number
        """
        doi = json_data.get('doi')
        return doi

    def get_title(self, json_data):
        """
        Extracts the title of the publication.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('title')

    def get_keywords(self, json_data):
        """
        Extracts the keywords from the json object. \n
        For now we take all keyword, but we could also choose type of keywords later \n
        Usual types: 'IEEE Keywords', 'INSPEC Controlled Indexing', 'INSPEC Non-Controlled Indexing', 'Author Keywords'
        that menas there are multiple types of keywords merged. Can do split when demanded.
        :param json_data: JSON object with meta data
        :return: List of strings
        """
        keywords_raw = json_data.get('keywords')
        keywords = []
        # iterate over all keyword-types
        for el in keywords_raw:
            keywords.extend(el.get('kwd'))
        return keywords

    def get_abstract(self, json_data):
        """
        Extracts the abstract from the publication.
        :param json_data: JSON object with meta data
        :return: String
        """
        return json_data.get('abstract')
