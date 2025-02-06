"""
Module for the concrete scraper class ScraperScienceDirect
"""

import re

from Research_Scraper_Code.scraper_types.scraper_abstract import ScraperAbstract


class ScraperScienceDirect(ScraperAbstract):
    """
    Class for the specific ScienceDirect Scraper
    """

    @property
    def domain(self):
        return 'linkinghub.elsevier.com'

    @property
    def domain2(self):
        return 'sciencedirect.com'

    @property
    def legal_params(self):
        legal_params = [
            'full',
            'main',
            'title',
            'doi',
            'keywords',
            'abstract'

        ]
        return legal_params

    def check_scrape_possible(self, url):
        # taking alternative domain into account
        alternative_possibility = self.domain2 in url
        return super().check_scrape_possible(url) or alternative_possibility

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
        super(ScraperScienceDirect, self).scrape_by_url(url, params)

        scrape_result = {'url': url}

        # params logic

        # check if params are legal otherwise raise error
        self.check_params_legal(params)

        if params is None:
            params = ['main']

        if params == ['main']:
            params = ['title', 'keywords', 'doi', 'abstract']

        if params == ['full']:
            params = self.legal_params  # full = all legal params

        # get soup for subsequent parsing, for ScienceDirect we use cloudscraper to bypass cloudflare
        bs = self.get_bs(url, method='cloud')

        # get title
        if 'title' in params:
            scrape_result['title'] = self.get_title(bs)

        # get doi
        if 'doi' in params:
            scrape_result['doi'] = self.get_doi(bs)

        # get keywords
        if 'keywords' in params:
            scrape_result['keywords'] = self.get_keywords(bs)

        # get abstract
        if 'abstract' in params:
            scrape_result['abstract'] = self.get_abstract(bs)

        # remove None values from result dict
        scrape_result = {key: value for key, value in scrape_result.items() if value is not None}

        return scrape_result

    def get_title(self, bs):
        """
        Get title of a publication
        :param bs: Bs4 object
        :return: String with title
        """
        title = bs.find('span', class_='title-text').text.strip()
        return title

    def get_doi(self, bs, doi_type='doi_number'):
        """
        Gets the doi_number of a publication
        :param bs: Bs4 object
        :return: String with doi_number
        """
        regex_doi = re.compile(r'http(s?)://doi.org/.*')
        doi_link = bs.find('a', class_='doi').text.strip()


        # switch logic for different doi types
        if doi_type == 'doi_number':
            # control and clean doi
            if regex_doi.match(doi_link):
                doi = re.sub(r'http(s?)://doi.org/', '', doi_link)
                return doi
            else:
                return None
        if doi_type == 'doi_link':
            if regex_doi.match(doi_link):
                return doi_link
            else:
                return None
        return None

    def get_keywords(self, bs):
        """
        Get list of keywords
        :param bs: Received bs of the publication
        :return: List of strings
        """
        keywords = []
        try:
            kwds = bs.find('div', class_='keywords-section').find_all('div', class_='keyword')
            for kwd in kwds:
                keyword = kwd.text.strip()
                keywords.append(keyword)
            return keywords
        except:
            return None

    def get_abstract(self, bs):
        """
        Get abstract of a publication
        :param bs: Received bs of the publication
        :return: Abstract : String with abstract
        """
        try:
            abstract = bs.find('div', class_='abstract author').div.text.strip()
            return abstract
        except:
            return None
