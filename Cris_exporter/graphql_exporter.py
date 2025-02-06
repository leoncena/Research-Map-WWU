import os
import time
import pymongo as pm
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport


class GraphqlExporter:

    GRAPHQL_TO_REGEX = "([A-Za-z].+)\(first:"  # Example https://regex101.com/r/JMTXsT/1
    GRAPHQL_URL = os.getenv("GRAPHQL_URL", 'https://cris-api.uni-muenster.de/')
    MONGODB_URI = os.getenv("CRISETL_ENV_MONGO_URI", 'mongodb://localhost:27017/')
    DATABASE = os.getenv("DATA_LAKE_DB_NAME", 'FLK_Data_Lake')

    def __init__(self, query_template_location: os.PathLike):
        """
        Prepare the exporter by loading the query template and the collection name.
        :param query_template_location: path to the query template
        """

        template_file = open(query_template_location, 'r')
        template_content = template_file.read()
        self.query_template = template_content
        template_file.close()


    def execute_graphql_query(self, query: str):
        """
        Execute a graphql query and return the result.
        :param query: graphql query
        :return: result of graphql query
        """
        base_time = 0.1
        time.sleep(base_time)
        for attempt in range(10):
            base_time = base_time * 2
            try:
                transport = AIOHTTPTransport(url=self.GRAPHQL_URL)
                client = Client(transport=transport, fetch_schema_from_transport=True, execute_timeout=400)
                result = client.execute(document=gql(query))
            except:
                time.sleep(base_time)
            else:
                break
        else:
            raise SystemExit(0)
        return result

    def make_pagination_query(self, after_cursor: str = None):
        """
        Generates the next graphql query for pagination.

        :param: query_template: name of the query template located in the queries' folder
        :param: after_cursor: cursor of the last object that is returned
        :return: graphQL query as string
        """
        return self.query_template.replace(
            'after: ""', 'after: "{}"'.format(after_cursor) if after_cursor else 'after: ""'
        )

    def insert_documents(self, database: str, db_collection: str,  documents: list, truncate_collection: bool = False):
        """
        Insert documents into the database.
        :param database: name of the database
        :param db_collection: name of the collection
        :param documents: documents to insert
        :param truncate_collection: truncate the collection before inserting
        """
        if not documents:
            return
        mongodb_instance = pm.MongoClient(self.MONGODB_URI, serverSelectionTimeoutMS=500000)
        database = mongodb_instance[database]
        print("Insert " + str(len(documents)) + " documents into collection: " + str(db_collection))
        if db_collection in database.list_collection_names() and truncate_collection:
            database[db_collection].delete_many({})  # delete all existing documents
        for chunk in self.__chunks(documents, 50000):
            database[db_collection].insert_many(chunk)
        mongodb_instance.close()

    def __chunks(self, lst: list, n: int):
        """
        Yield successive n-sized chunks from lst.
        :param lst: list to chunk
        :param n: number of elements per chunk
        :return: chunks of the list
        """
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
