import os
import pymongo as pm
from graphql_exporter import GraphqlExporter
from re import findall


class GraphqlListExporter(GraphqlExporter):

    def __init__(self, query_template_location: os.PathLike):
        """
        Prepare the exporter by setting creating a GraphqlExporter, setting the cursor and setting the has_next_page flag.
        :param query_template_location:
        """
        super().__init__(query_template_location)
        self.has_next_page = True
        self.after_cursor = None
        db_collection = findall(self.GRAPHQL_TO_REGEX, self.query_template)
        if db_collection is None:
            raise ValueError("The file " + (os.path.basename(query_template_location)) + " has no list object")
        json_list_name = str(db_collection[0])
        self.db_collection = json_list_name.replace("List", '')

    def export(self):
        """
        Export all pages of the GraphQL list and inserts them into the database.
        :return: None
        """
        documents = []
        while self.has_next_page:
            page_documents = self.__export_page()
            documents.extend(page_documents)

        self.insert_documents(self.DATABASE, self.db_collection, documents, True)
        self.create_index()

    def __export_page(self):
        """
        Export one page of the list.
        :return: list of documents
        """
        documents = []
        query = self.make_pagination_query(self.after_cursor)
        result = self.execute_graphql_query(query)
        json_list_name = self.db_collection + 'List'
        self.after_cursor = result[json_list_name]['pageInfo']['endCursor']
        self.has_next_page = result[json_list_name]['pageInfo']['hasNextPage']
        for list_element in result[json_list_name]['list']:
            documents.append(list_element['node'])

        return documents

    def create_index(self):
        """
        Create an index on the id field of the collection.
        :return: None
        """
        mongodb_instance = pm.MongoClient(self.MONGODB_URI, serverSelectionTimeoutMS=500000)
        database = mongodb_instance[self.DATABASE]
        database[self.db_collection].create_index("id", unique=True)