import os
import pymongo as pm
from graphql_exporter import GraphqlExporter
from re import findall


class GraphqlConnectionExporter(GraphqlExporter):
    GRAPHQL_CONNECTION_REGEX = "([A-Za-z].+)\(id:"  # Example https://regex101.com/r/tt4tJG/1

    def __init__(self, query_template_location: os.PathLike):
        """
        Prepare the exporter by setting creating a GraphqlExporter.
        :param query_template_location:
        """
        super().__init__(query_template_location)
        self.id_to_export = None
        self.after_cursor = None
        self.has_next_page = True
        from_collection_names = findall(self.GRAPHQL_CONNECTION_REGEX, self.query_template)
        self.from_collection_name = from_collection_names[0]
        db_collections = findall(self.GRAPHQL_TO_REGEX, self.query_template)
        self.to_collection_name = db_collections[0]

        db_collection = findall(self.GRAPHQL_TO_REGEX, self.query_template)
        if db_collection is None:
            raise ValueError("The file " + (os.path.basename(query_template_location)) + " has no list object")
        json_list_name = str(db_collection[0])
        self.to_collection_name = json_list_name.replace("List", '')
        self.collection_name = self.from_collection_name + "_" + self.to_collection_name
        self.exporter_collection_name = 'exporter_' + self.collection_name
        self.__make_exporter_collection()

    def __make_exporter_collection(self):
        """
        Create the exporter collection.
        :return:
        """
        mongodb_instance = pm.MongoClient(self.MONGODB_URI, serverSelectionTimeoutMS=300000)
        database = mongodb_instance[self.DATABASE]
        if self.exporter_collection_name in database.list_collection_names():
            exporter_ids = list(database[self.exporter_collection_name].find({}, {"id": 1, "_id": 0}))
            if len(exporter_ids) == 0:
                from_collection_ids = list(database[self.from_collection_name].find({}, {"id": 1, "_id": 0}))
                database[self.exporter_collection_name].insert_many(from_collection_ids)
        else:
            from_collection_ids = list(database[self.from_collection_name].find({}, {"id": 1, "_id": 0}))
            database[self.exporter_collection_name].insert_many(from_collection_ids)
            database[self.collection_name].delete_many({})
        mongodb_instance.close()

    def export(self):
        """
        Export connections of the GraphQL list and inserts them into the database.
        :return: None
        """
        exporter_collection_name = 'exporter_' + self.collection_name
        mongodb_instance = pm.MongoClient(self.MONGODB_URI, serverSelectionTimeoutMS=300000)
        database = mongodb_instance[self.DATABASE]
        from_ids = list(database[exporter_collection_name].find({}, {"id": 1, "_id": 0}))
        mongodb_instance.close()

        for id_dict in from_ids:
            self.has_next_page = True
            self.after_cursor = None
            self.id_to_export = id_dict['id']
            while self.has_next_page:
                self.__export_page()
            mongodb_instance = pm.MongoClient(self.MONGODB_URI, serverSelectionTimeoutMS=300000)
            database = mongodb_instance[self.DATABASE]
            database[exporter_collection_name].delete_one({"id": self.id_to_export})
        self.__drop_exporter_collection()
        self.create_indexes()

    def __export_page(self):
        """
        Export one page of the list.
        :return: list of documents
        """
        documents = []
        query = self.__make_connection_query()
        result = self.execute_graphql_query(query)
        self.after_cursor = result[self.from_collection_name]['connections'][self.to_collection_name]['pageInfo'][
            'endCursor']
        self.has_next_page = result[self.from_collection_name]['connections'][self.to_collection_name]['pageInfo'][
            'hasNextPage']
        connections = result[self.from_collection_name]['connections'][self.to_collection_name]['edges']
        for connection in connections:
            to_id = connection['node']['id']
            document = {self.from_collection_name + '_id': self.id_to_export, self.to_collection_name[:-1] + '_id': to_id}
            documents.append(document)
        self.insert_documents(self.DATABASE, self.collection_name, documents)

    def __make_connection_query(self):
        """
        Create the queries to fetch connections from graphql.

        :return: graphQL query as string
        """
        query = self.make_pagination_query(self.after_cursor)
        query = query.replace(
            'id: ""', 'id: "{}"'.format(str(self.id_to_export))
        )
        return query

    def __drop_exporter_collection(self):
        """
        Drop the exporter collection.
        :return:
        """
        mongodb_instance = pm.MongoClient(self.MONGODB_URI, serverSelectionTimeoutMS=300000)
        database = mongodb_instance[self.DATABASE]
        if self.exporter_collection_name in database.list_collection_names():
            database[self.exporter_collection_name].drop()
        mongodb_instance.close()

    def create_indexes(self):
        """
        Create indexes for the collection.
        :return:
        """
        mongodb_instance = pm.MongoClient(self.MONGODB_URI, serverSelectionTimeoutMS=300000)
        database = mongodb_instance[self.DATABASE]
        database[self.collection_name].create_index([(self.from_collection_name + '_id', pm.ASCENDING)])
        database[self.collection_name].create_index([(self.to_collection_name[:-1] + '_id', pm.ASCENDING)])
        mongodb_instance.close()