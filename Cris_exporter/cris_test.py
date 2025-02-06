import pathlib
import unittest
import re
import pymongo as pm

from os import path, getenv
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

class CrisExporterTest(unittest.TestCase):
    MONGODB_URI = getenv("CRISETL_ENV_MONGO_URI", 'mongodb://localhost:27017/')
    DATABASE = getenv("DATA_LAKE_DB_NAME", 'FLK_Data_Lake')
    GRAPHQL_URL = getenv("GRAPHQL_URL", 'https://cris-api.uni-muenster.de/')
    TEST_QUERY = """
        query {
            publicationList {
                list {
                    node {
                        id
                    }
                }
            }
        }"""

    def test_mongodb_connection(self):
        """
        Test if MongoDB connection is possible.
        """

        client = pm.MongoClient(self.MONGODB_URI)
        info = client.server_info()
        assert (info["ok"] == 1.0)
        db_list = client.list_database_names()
        assert (self.DATABASE in db_list)

    def test_graphql_connection(self):
        """
        Test if GraphQL connection is possible.
        :return:
        """
        transport = AIOHTTPTransport(self.GRAPHQL_URL)
        client = Client(transport=transport, fetch_schema_from_transport=True, execute_timeout=400)
        result = client.execute(document=gql(self.TEST_QUERY))
        assert (type(result) is dict)


    def test_graphql_queries(self):
        """
        Test all queries in the folder queries.
        :return:
        """
        dir_path = path.dirname(path.realpath(__file__))
        graphql_queries_folder = path.join(dir_path, 'queries')
        transport = AIOHTTPTransport(self.GRAPHQL_URL)
        schema_path = path.join(graphql_queries_folder, 'schema.graphql')
        with open(schema_path, 'r') as schema_file:
            schema = schema_file.read()
        client = Client(transport=transport, schema=schema, execute_timeout=400)
        for query_template in pathlib.Path(graphql_queries_folder).glob('**/*'):
            if ".graphqlconfig" in str(query_template) or "schema.graphql" in str(query_template):
                continue
            with open(query_template, 'r') as query_file:
                query = gql(query_file.read())
                client.validate(query)

    def test_name_convention(self):
        dir_path = path.dirname(path.realpath(__file__))
        graphql_queries_folder = path.join(dir_path, 'queries')
        schema_path = path.join(graphql_queries_folder, 'schema.graphql')
        for query_template in pathlib.Path(graphql_queries_folder).glob('**/*'):
            if ".graphqlconfig" in str(query_template.name) or "schema.graphql" in str(query_template.name):
                continue
            if "get_connection_" in str(query_template.stem):
                file_name_paths = str(query_template.stem).split('_')
                gql_object_types = file_name_paths[2:4]
                for gql_object_type in gql_object_types:
                    gql_object_type = gql_object_type[0].upper() + gql_object_type[1:]
                    self.gql_object_type_exists(gql_object_type, schema_path)
                continue
            if "get_" in str(query_template.stem):
                file_name_paths = str(query_template.stem).split('_')
                gql_object_type = file_name_paths[1]
                gql_object_type = gql_object_type[0].upper() + gql_object_type[1:-1] + "List"
                self.gql_object_type_exists(gql_object_type, schema_path)
                continue

            assert "The Filename " + query_template.stem + " does not follow naming convention."

    def gql_object_type_exists(self, gql_object_type, schema_path):
        """
        Check if the gql_object_type exists in the schema.
        :param gql_object_type: Name of the object type
        :param schema_path: Path to the schema
        :return:
        """
        regex = r"type " + gql_object_type + r" {"
        with open(schema_path, 'r') as schema_file:
            schema = schema_file.read()
        assert re.search(regex, schema), f"The object type {gql_object_type} does not exist in the schema."

if __name__ == '__main__':
    unittest.main()
