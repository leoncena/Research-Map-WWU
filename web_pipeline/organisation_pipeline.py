import pymongo as pm
import os

class OrganisationPipeline:
    MONGODB_FROM_URI = os.getenv('PIPELINE_ENV_MONGODB_FROM_URI', "mongodb://localhost:27017/")
    MONGODB_TO_URI = os.getenv('PIPELINE_ENV_MONGODB_TO_URI', "mongodb://localhost:27017/")
    MONGODB_FROM_DB = "FLK_Data_Lake"
    MONGODB_TO_DB = "FLK_Web"

    def __init__(self, mongodb_from_uri: str, mongodb_from_database: str, mongodb_to_uri: str,
                 mongodb_to_database: str):
        self.MONGODB_FROM_URI = mongodb_from_uri
        self.MONGODB_FROM_DB = mongodb_from_database
        self.MONGODB_TO_URI = mongodb_to_uri
        self.MONGODB_TO_DB = mongodb_to_database

    def export_organisations(self, organisation_id: int):
        """
        Export organisations from data lake to web database.
        :param organisation_id: Organisation ID that is the head of the organisation hierarchy.
        :return: None
        """

        # Get all organisation ids that should be exported
        organisation_ids = get_all_hierarchy_organisation_ids(organisation_id, self.MONGODB_FROM_URI, self.MONGODB_FROM_DB)

        # Get all selected organisations from data lake
        mongo_client = pm.MongoClient(self.MONGODB_FROM_URI)
        from_db = mongo_client[self.MONGODB_FROM_DB]
        organisations = from_db['organisation']
        organisations_to_export = list(organisations.find({"id": {"$in": organisation_ids}}))
        mongo_client.close()

        # Export organisations to web database
        mongo_client = pm.MongoClient(self.MONGODB_TO_URI)
        to_db = mongo_client[self.MONGODB_TO_DB]
        organisations = to_db['organisations']
        organisations.delete_many({})
        organisations.insert_many(organisations_to_export)
        mongo_client.close()


def get_all_hierarchy_organisation_ids(organisation_id: int, mongodb_from_uri: str, mongodb_from_db: str):
    """
    Get all hierarchy organisation ids from the data lake.
    :param organisation_id: Organisation ID that is the head of the organisation hierarchy.
    :param mongodb_from_uri: URI of the data lake database server.
    :param mongodb_from_db: Name of the data lake database.
    :return: List of hierarchy organisation ids for the given organisation.
    """

    organisation_ids = []
    # Get all organisation ids that should be exported
    mongo_client = pm.MongoClient(mongodb_from_uri)
    from_db = mongo_client[mongodb_from_db]
    organisations_hierarchy = from_db['organisation_organisation']
    for child_id in organisations_hierarchy.find({"organisation_id": str(organisation_id)}):
        child_id = child_id['child_organisation_id']
        organisation_ids.append(child_id)
        organisation_ids.extend(get_all_hierarchy_organisation_ids(child_id, mongodb_from_uri, mongodb_from_db))
    mongo_client.close()
    return organisation_ids
