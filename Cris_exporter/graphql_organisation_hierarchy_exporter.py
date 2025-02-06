from graphql_exporter import GraphqlExporter
import pymongo as pm
import os


class GraphqlOrganisationHierarchyExporter(GraphqlExporter):

    def __init__(self, query_template_location: os.PathLike):
        """
        Constructor.
        """
        super().__init__(query_template_location)
        self.collection_name = "organisation_organisation"
        self.organisation_id = ""

    def export(self):
        """
        Export the organisation hierarchy.
        """
        documents = []
        mongodb_instance = pm.MongoClient(self.MONGODB_URI, serverSelectionTimeoutMS=300000)
        database = mongodb_instance[self.DATABASE]
        organisations = list(database['organisation'].find({}, {"id": 1, "_id": 0}))
        mongodb_instance.close()
        for organisation in organisations:
            self.organisation_id = organisation['id']
            organisation_documents = self.export_organisation()
            documents.extend(organisation_documents)

        self.insert_documents(self.DATABASE, self.collection_name, documents, True)

    def export_organisation(self):
        """
        Export a single organisation.
        :return:
        """
        documents = []
        query = self.__make_connection_query()
        result = self.execute_graphql_query(query)

        child_organisations = result['organisation']['connections']['organisations']['edges']
        for child_organisation in child_organisations:
            child_organisation_id = child_organisation['node']['id']
            documents.append({'organisation_id': self.organisation_id, 'child_organisation_id': child_organisation_id})
        return documents

    def __make_connection_query(self):
        """
        Create the queries to fetch connections from grpahql.

        :param cris_id: cris_id to which the connections should be found
        :return: graphQL query as string
        """
        query = self.query_template.replace(
            'id: ""', 'id: "{}"'.format(str(self.organisation_id))
        )
        return query
