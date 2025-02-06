"""
Module for the abstract scraper class.

Comments:
    - This module contains the abstract scraper class.
    - This class is the parent class for all scraper classes.
    - This class contains the abstract methods that must be implemented by all scraper classes.
    - In the first version we try to avoid using helium/ selenium.
"""

from abc import ABC, abstractmethod

import cloudscraper
import requests
from bs4 import BeautifulSoup


class ScraperAbstract(ABC):
    """
    Abstract scraper class for all scrapers
    """

    @property
    @abstractmethod
    def domain(self):
        """
        Abstract property for the legal domain of the scraper.
        """
        pass

    @property
    @abstractmethod
    def legal_params(self):
        """
        Legal params for thr scraper
        """
        pass

    @abstractmethod
    def scrape_by_url(self, url, params=None):
        """
        Abstract method for scraping a publication by a url.
        """
        if not self.check_scrape_possible(url):
            raise Exception(f'This scraper cannot scrape this url: {url}')

    def check_scrape_possible(self, url):
        """
        Checks if the scraper can scrape the given url

        :param url: URL of a publication
        :return: Boolean
        """
        possible = self.domain in url
        return possible

    def check_params_legal(self, params):
        """
        Checks if the params are legal and raised error in that case
        :param params: params for scraping
        :return: Bool
        """
        if params is not None:  # cannot iterate over None object -> check it beforehand
            for param in params:
                if param not in self.legal_params:
                    raise ValueError(f'Param \'{param}\' is not legal. Legal params are: {self.legal_params}')

    def get_page_with_requests(self, url):
        """
        Requests a page and returns the response
        :param url: URL of a publication
        :return: Response object
        """

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15'}
        response = requests.get(url, headers=headers, timeout=30)
        assert response.status_code == 200
        return response

    def get_page_with_cloudscraper(self, url):
        """
        Requests a with cloudscraoer page and returns the response
        :param url: URL of a publication
        :return: Response object
        """

        scraper = cloudscraper.create_scraper(
            browser={
                'custom': 'ScraperBot/1.0',
            }
        )
        response = scraper.get(url)
        assert response.status_code == 200
        return response

    def get_bs(self, url, method='requests'):
        """
        Returns the Beatiful Soup (BS) object of a URL \n
        It downloads the HTML of the URL and parses it with BS

        Comments:
           - More types will be added in future if needed
        :param url: URL of a publication
        :param method: Method of a HTML downlaod (requests, cloud)
        :return: BS object
        """
        try:
            if method == 'requests':
                request = self.get_page_with_requests(url)
                bs = BeautifulSoup(request.content, 'html.parser')
            elif method == 'cloud':
                request = self.get_page_with_cloudscraper(url)
                bs = BeautifulSoup(request.content, 'html.parser')
            else:
                raise ValueError(f'Method {method} not supported')

        except Exception as e:
            # todo Specify error after testing
            print(f'[Error caught- scraper_abstract.py: get_bs] : {e}', url)
            return None

        return bs


