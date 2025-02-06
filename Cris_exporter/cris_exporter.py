import pathlib
import os
from os import path


from graphql_list_exporter import GraphqlListExporter
from graphql_connenction_exporter import GraphqlConnectionExporter
from graphql_organisation_hierarchy_exporter import GraphqlOrganisationHierarchyExporter


GRAPHQL_TO_REGEX = "([A-Za-z].+)\(first:"  # Example https://regex101.com/r/JMTXsT/1
GRAPHQL_NODE_CONTENT_REGEX = "list\s*{\s*node\s*{([a-zA-z0-9\s*]*)"  # Example https://regex101.com/r/v0b9RE/1
GRAPHQL_CONNECTION_REGEX = "([A-Za-z].+)\(id:"  # Example https://regex101.com/r/tt4tJG/1

ORGANISATION_HIERARCHY_QUERY = """query {
                            organisation(id: "") {
                                connections {
                                    organisations {
                                        edges {
                                            node {
                                                id
                                            }
                                        }
                                    }
                                }
                            }
                        }"""

class CrisExporter:
    """
    Exporter to regularly export data from the cris system to the  Data Lake

    """

    def export_lists(self):
        """
        Export the data via the lists.
        :return:
        """
        dir_path = path.dirname(path.realpath(__file__))
        graphql_queries_folder = os.path.join(dir_path, 'queries')

        for query_template in pathlib.Path(graphql_queries_folder).glob('**/*'):
            filename = query_template.name
            if "get_" not in filename or "connection" in filename or "hierarchy" in filename:
                continue

            exporter = GraphqlListExporter(query_template)
            exporter.export()

    def export_connections(self):
        """
        Export the data via the connections.
        :return:
        """
        dir_path = path.dirname(path.realpath(__file__))
        graphql_queries_folder = os.path.join(dir_path, 'queries')

        for query_template in pathlib.Path(graphql_queries_folder).glob('**/*'):
            filename = query_template.name
            if "get_" not in filename or "connection" not in filename:
                continue

            exporter = GraphqlConnectionExporter(query_template)
            exporter.export()

    def export_organisation_hierarchy(self):
        """
        Export the organisation hierarchy.
        :return:
        """
        dir_path = path.dirname(path.realpath(__file__))
        graphql_queries_folder = os.path.join(dir_path, 'queries')

        for query_template in pathlib.Path(graphql_queries_folder).glob('**/*'):
            filename = query_template.name
            if "organisations_hierarchy" not in filename:
                continue
            exporter = GraphqlOrganisationHierarchyExporter(query_template)
            exporter.export()