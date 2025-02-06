"""
Module for the class if the scraper
"""
import time

import pandas as pd

from Research_Scraper_Code import utils
from Research_Scraper_Code.scraper_types.scraper_ieee import ScraperIEEE
from Research_Scraper_Code.scraper_types.scraper_sciencedirect import ScraperScienceDirect
from Research_Scraper_Code.scraper_types.scraper_springer import ScraperSpringer


# from scholarly import scholarly, ProxyGenerator
# import pandas as pd


class ResearchScraper:
    """
    Research scraper that handles multiple specialised scrapers and can be extended easily
    """

    # initialize the class with all the scrapers
    def __init__(self):
        # here one cann add another scraper  (of course after importing the script above)
        self.all_scraper = [ScraperSpringer(), ScraperScienceDirect(), ScraperIEEE()]

    def scrape_publication_by_url(self, url, params):
        """
        Scrapes a publication by a given url
        :param url: URL of the publication
        :param params: Parameter for scraping
        :return: Dict with results
        """

        try:
            self.__check_params_type(params)  # check format of params

            # check if url is valid or a doi
            if utils.check_if_doi_link(url):
                print(f'URL (\'{url}\') is a DOI link, Links is now resolved properly')
                url = utils.resolve_url(url)

                # check if doi could be resolved
                if 'doi.org' in url:
                    print(f'URL (\'{url}\') could not be resolved to a valid link')
                    return None

                print(f'Resolved DOI link to: {url}')

            result = {}

            scraper_found = False

            # search suitable scraper
            for scraper in self.all_scraper:
                if scraper.check_scrape_possible(url):
                    msg = f'[DEBUG - ResearchScraper] - Found scraper for {url} -> {type(scraper).__name__}'
                    # print green background
                    print('\x1b[6;30;42m' + msg + '\x1b[0m')
                    scraper_found = True
                    result = scraper.scrape_by_url(url, params)
                    break

            # if no scraper was found return None
            if not scraper_found:
                msg = f'[DEBUG - ResearchScraper] - No scraper found for {url}'
                # print orange background black font
                print('\x1b[6;30;43m' + msg + '\x1b[0m')
                # return only url for logging purposes
                return {'error': 'No scraper found for this url', 'url': url}

            # dict keys whose values are not none
            not_none_keys = [key for key, value in result.items() if value is not None]

            msg = f' Scraped keys: {not_none_keys}'
            # print green font
            print('\x1b[6;30;32m' + msg + '\x1b[0m')
            return result
        except Exception as e:
            print('\n\n unknown error caught', e)
            return {'error': str(e), 'error_url': url}

    def scrape_publication_by_doi(self, doi, params):
        """
        Scrapes a publication by a given doi
        :param doi: DOI of a publication
        :param params: Parameter for scraping
        :return: Dict with results
        """
        # check if it is a doi
        if not utils.check_if_doi_number(doi):
            return {'error': 'no valid doi passed', 'error_doi': doi}
        url = utils.create_doi_link(doi)
        if url is None:
            return {'error': 'url could not be resolved for DOI', 'error_doi': doi}
        return self.scrape_publication_by_url(url, params)

    # this functions not used, considering removing
    def scrape_publication_by_doi_list(self, doi_list, params=['full']):
        """
        Scrapes a list of publication by its DOI numbers
        :param doi_list: List of DOI numbers
        :param params: Parameter for scraping
        :return: List of dicts with results
        """

        start = time.time()
        print(f'Time of scrape start: {time.strftime("%Y_%m_%d__%H_%M")}')
        results = []
        for idx, doi in enumerate(doi_list):
            scraping_log = f'>>> Scraping {doi} #{idx}'
            # print blue background with black font
            print('\x1b[6;30;44m' + scraping_log + '\x1b[0m')
            result = self.scrape_publication_by_doi(doi, params)
            print(f'>>>> Scraping {doi} done')
            results.append(result)
            print(f'>>>> Scraping {doi} added to results')
        print(f'>>>> Scraping {len(doi_list)} publications done')
        utils.write_results(results, f'scrapings_{time.strftime("%Y_%m_%d__%H_%M")}')
        print(f'Time of scrape end: {time.strftime("%Y_%m_%d__%H_%M")}')
        end = time.time()
        print(f'Total time took: {round((end - start) / 60, 2)} minutes')
        return results

    # this functions not used, considering removing (used in test script only)
    def scrape_publication_by_mongo_id(self, mongo_id, params=['full']):
        f"""
        Scrapes a publication by its mongo id \n
        Method and Comments:
         - First looks for a DOI number and then for a URL \n
         - Has a source flag if information are saved for legal reasons
         - This can be used later if scopus search without success in data pipeline
        :param mongo_id: ID of the publication in the mongoDB
        :param params: Scraping params
        :return: Scraping resullt in dict of form mongo_id:result
        """
        final_result = {'id': mongo_id, 'scraping_result': None}

        # get data from mongo
        publication_mongo_data = utils.queryMongoDB_publication(mongo_id)
        if publication_mongo_data is None:
            return {'id': mongo_id, 'result': None, 'error': 'No data found in mongoDB'}

        # check if there is a DOI
        if publication_mongo_data.get('doi') is not None:
            # status debug print
            print(
                f'[Research_Scraper.py : scrape_publication_by_mongo_id] Found DOI in mongoDB: {publication_mongo_data.get("doi")}')
            doi = publication_mongo_data.get('doi')
            scraping_result = self.scrape_publication_by_doi(doi, params)
            final_result = {'id': mongo_id,
                            'scraping_result': scraping_result
                            }
            # add source flag to scraping results
            final_result['scraping_result']['data_source'] = 'scraping-doi'

        # check if there is a URL
        elif publication_mongo_data.get('cfUri') is not None:
            # status debug print
            print(
                f'[Research_Scraper.py : scrape_publication_by_mongo_id] Found URL in mongoDB: {publication_mongo_data.get("cfUri")}')
            url = publication_mongo_data.get('cfUri')
            scraping_result = self.scrape_publication_by_url(url, params)
            final_result = {'id': mongo_id,
                            'scraping_result': scraping_result
                            }
            # add scource flag to scraping results
            final_result['scraping_result']['data_source'] = 'scraping-url'

        # if both do not exist return None and describe in error
        else:
            # status debug print in red
            print('\x1b[6;30;41m' +
                  f'[Research_Scraper.py : scrape_publication_by_mongo_id] No DOI or URL found in mongoDB - Mongo ID: {mongo_id}' +
                  '\x1b[0m')

            final_result = {'id': mongo_id,
                            'scraping_result': None,
                            'error': 'No DOI or URL found in mongoDB'}

        return final_result

    # this functions not used, considering removing (used in test script only)
    def scrape_publications_from_mongo_df(self, df, params=['full']):
        """
        Scrapes a list of publications from a pandas df \n
        Scrapes by DOI or URL if DOI is not available \n
        :param df: Pandas dataframe with publications
        :param params: Parameter for scraping
        :return: List of dicts with results
        """
        final_results = []
        counter = 1
        for index, row in df.iterrows():
            try:
                # if row.get('doi') is not None or row.get('cfUri') is not None:
                # if doi is not Nan or cfuri is not NaN
                if pd.notna(row.get('doi')) or pd.notna(row.get('cfUri')):

                    row_result = {'id': row.get('id'), 'scraping_result': None}

                    # check if there is a DOI
                    # if row.get('doi') is not None:
                    if pd.notna(row.get('doi')):
                        # status debug print
                        print(f'[Research_Scraper.py : scrape_publications_from_mongo_df] #{counter}: Found DOI in DF: '
                              f'{row.get("doi")}')

                        doi = row.get('doi')
                        scraping_result = self.scrape_publication_by_doi(doi, params)
                        # add source flag to scraping results
                        scraping_result['data_source'] = 'scraping-doi'
                        row_result['scraping_result'] = scraping_result


                    # check if there is a URL
                    # elif row.get('cfUri') is not None:
                    elif pd.notna(row.get('cfUri')):
                        # status debug print
                        print(f'[Research_Scraper.py : scrape_publications_from_mongo_df] #{counter}: Found URL in DF: '
                              f'{row.get("cfUri")}')
                        url = row.get('cfUri')
                        scraping_result = self.scrape_publication_by_url(url, params)
                        scraping_result['data_source'] = 'scraping-url'
                        row_result['scraping_result'] = scraping_result

                    # add result to final results list
                    final_results.append(row_result)
                else:
                    # if both do not exist return None and describe in error

                    # status debug print in red
                    pub_id = row.get('id')
                    print('\x1b[6;30;41m' +
                          f'[Research_Scraper.py : scrape_publications_from_mongo_df] #{counter}: No DOI or URL found in DF -  ID: '
                          f'{pub_id}' +
                          '\x1b[0m')
                    scraping_result = None
                    row_result = {
                        'id': row.get('id'),
                        'scraping_result': None,
                        'error': 'No DOI or URL found in DF'
                    }
                    final_results.append(row_result)
                counter += 1
            except Exception as e:
                msg = f' [Research_Scraper.py : scrape_publications_from_mongo_df] Error - {e} -  scraping ' \
                      f'publication with ID: {row.get("id")} '
                # print in red
                print('\x1b[6;30;41m' + msg + '\x1b[0m')
                pass

        return final_results

    def __check_params_type(self, params):
        """
        Checks the type of params and raises errors if necessary \n
        Params must be a list of strings
        :param params: Parameter for scraping
        :return: void, raises errors if necessary
        """
        # check format of params
        if not isinstance(params, list):
            raise Exception('Input "params" must be a list')
        for param in params:
            if not isinstance(param, str):
                raise Exception('"Params" must consist only of strings')

    def scrape_publication_by_doi_and_url(self, doi, url, params=['full']):
        f"""
        Scrapes a publication by doi or url \n
        Since this method is called by a aggregated fill method we only return results and not ids of publications \n
        Method and Comments:
         - First looks for a DOI number and then for a URL \n
         - Has a source flag if information are saved for legal reasons
         - This can be used later if scopus search without success in data pipeline
        :param doi: DOI number of a publication
        :param url: URL of a publication
        :param params: Scraping params
        :return: Scraping result in dict
        """
        final_result = {'scraping_result': None}

        # get data from mongo
        entered_publication_data = {
            'doi': doi,
            'cfUri': url
        }
        if entered_publication_data is None:
            return {'scraping_result': None, 'error': 'No data entered'}

        # check if there is a DOI
        if entered_publication_data.get('doi') is not None:
            # status debug print
            print(
                f'[Research_Scraper.py : scrape_publication_by_doi_and_url] No DOI entered: {entered_publication_data.get("doi")}')
            doi = entered_publication_data.get('doi')
            scraping_result = self.scrape_publication_by_doi(doi, params)
            final_result = {'scraping_result': scraping_result
                            }
            # add source flag to scraping results
            final_result['scraping_result']['data_source'] = 'scraping-doi'

        # check if there is a URL
        elif entered_publication_data.get('cfUri') is not None:
            # status debug print
            print(
                f'[Research_Scraper.py : scrape_publication_by_doi_and_url] URL entered: {entered_publication_data.get("cfUri")}')
            url = entered_publication_data.get('cfUri')
            scraping_result = self.scrape_publication_by_url(url, params)
            final_result = {'scraping_result': scraping_result
                            }
            # add scource flag to scraping results
            final_result['scraping_result']['data_source'] = 'scraping-url'

        # if both do not exist return None and describe in error
        else:
            # status debug print in red
            print('\x1b[6;30;41m' +
                  f'[Research_Scraper.py : scrape_publication_by_mongo_id] No DOI or URL found entered' +
                  '\x1b[0m')

            final_result = {'scraping_result': None,
                            'error': 'No DOI or URL entered'}

        return final_result['scraping_result']
