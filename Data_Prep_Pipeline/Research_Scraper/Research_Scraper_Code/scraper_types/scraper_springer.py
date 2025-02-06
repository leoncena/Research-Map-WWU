"""
Module for the concrete scraper class for Springer
"""

import json

from Research_Scraper_Code import utils
from Research_Scraper_Code.scraper_types.scraper_abstract import ScraperAbstract


class ScraperSpringer(ScraperAbstract):
    """
    Class for the specific Springer Scraper
    """

    @property
    def domain(self):
        """
        Domain of the scraper
        :return:
        """
        return 'link.springer.com'

    @property
    def legal_params(self):
        """
        Legal params for this scraper
        :return:
        """
        legal_params = [
            'full',
            'main',
            'title',
            'doi',
            'keywords',
            'abstract'
        ]
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

        # check if scraper can scrape this url (defined in super method)
        # raise error if not
        super(ScraperSpringer, self).scrape_by_url(url, params)

        # if not self.check_scrape_possible(url):
        #     raise Exception("This scraper cannot scrape this url")

        scrape_result = {'url': url}  # first add the url to the result

        # params logic

        # check if params are legal
        self.check_params_legal(params)

        if params is None:
            params = ['main']

        # currently main has all the params, may change in the future
        if params == ['main']:
            params = ['title', 'keywords', 'doi', 'abstract']

        if params == ['full']:
            params = self.legal_params  # full means all legal params

        # get soup for subsequent parsing
        bs = self.get_bs(url)
        json_data = self.get_json_data(bs)

        if 'title' in params:
            scrape_result['title'] = self.get_title(bs)

        if 'doi' in params:
            scrape_result['doi'] = self.get_doi(url)

        if 'keywords' in params:
            scrape_result['keywords'] = self.get_keywords(bs)

        if 'abstract' in params:
            scrape_result['abstract'] = self.get_abstract(url, json_data)

        # remove None values from result dict
        scrape_result = {key: value for key, value in scrape_result.items() if value is not None}

        return scrape_result

    def get_json_data(self, bs):
        """
        Access the json data from the website
        :param bs: BS object
        :return: json data
        """
        try:
            json_string = bs.find('script', {'type': 'application/ld+json'}).text
        except:
            return {}
        json_data = json.loads(json_string)

        if '{"mainEntity":' in json_string:
            return json_data['mainEntity']
        return json_data

    def get_doi(self, url):
        """
        Extract the DOI from the URL
        :param url: URL of a publication
        :return: DOI number
        """
        url_splitted = url.split('/')  # split url with '/' to find where DOI is
        doi_number = url_splitted[-2] + '/' + url_splitted[-1]
        if utils.check_if_doi_number(doi_number):
            return doi_number
        else:
            return None

    def get_title(self, bs):
        """
        Returns title of a publication
        :param bs: BS object
        :return: String with title
        """
        try:
            title = bs.find('h1', {'class': 'c-article-title'}).text.strip()
            return title
        except:
            return None

    def get_keywords(self, bs):
        """
        Return list of keywords from json data
        :param bs: BS object
        :return: List of keywords
        """

        keywords = []
        try:
            kwds = bs.find('ul', class_='c-article-subject-list').find_all('li',
                                                                           class_='c-article-subject-list__subject')

            # clean keywords
            for kwd in kwds:
                keyword = kwd.text.strip()
                keywords.append(keyword)
            return keywords
        except:
            print('Error: No keywords found')
            return None

    def get_abstract(self, url, json_data):
        """
        Returns the abstract of the articles, books/proceedings do not have abstracts.
        :param url: Received url of the publication
        :param json_data: Received json data of publication
        :return: String with abstract
        """
        if '/book/' in url:
            return None

        try:
            abstract = json_data.get('description').strip()
            return abstract
        except:
            print("Error: no abstract found")
            return None
