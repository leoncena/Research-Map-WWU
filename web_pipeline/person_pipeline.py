import pymongo as pm
import os

class PersonPipeline:
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

    def export_persons(self, organisation_id: int):
        """
        Exports all persons of a given organisation to the Web database.
        :param organisation_id: The organisation id of the organisation to export the persons from.
        :return:
        """
        persons = self.add_publications_to_persons()
        self.export_persons_to_mongodb(persons)
        self.remove_persons_without_publications()

    def get_all_persons_of_hierarchy(self, organisation_ids: list):
        """
        Gets all persons for a given list organisation ids.
        :param organisation_ids: organisation ids to which the persons belong.
        :return: list of persons
        """
        # Connect to MongoDB
        client = pm.MongoClient(self.MONGODB_FROM_URI)
        db = client[self.MONGODB_FROM_DB]
        # Get all persons of the hierarchy
        persons_organisations = list(db["organisation_persons"].find({"organisation_id": {"$in": organisation_ids}}))
        person_ids = [person_organisation["person_id"] for person_organisation in persons_organisations]
        persons = list(db["person_with_pub"].find({"id": {"$in": person_ids}}))
        # Close connection
        client.close()
        return persons

    def export_persons_to_mongodb(self, persons):
        """
        Exports all persons to the Web database.
        :param persons: The persons to export.
        :return:
        """
        # Connect to MongoDB
        client = pm.MongoClient(self.MONGODB_TO_URI)
        db = client[self.MONGODB_TO_DB]
        # Export persons
        db["persons"].delete_many({})
        db["persons"].insert_many(persons)
        # Close connection
        client.close()

    def add_publications_to_persons(self):
        """
        Adds the publications to the persons.
        :return:
        """
        # Connect to MongoDB
        client = pm.MongoClient(self.MONGODB_TO_URI)
        db = client[self.MONGODB_FROM_DB]
        # Add publications to persons
        persons = list(db["person"].aggregate([
            {
                '$lookup': {
                    'from': 'person_publications',
                    'localField': 'id',
                    'foreignField': 'person_id',
                    'as': 'publicationList'
                }
            }, {
                '$unset': 'publicationList.person_id'
            }, {
                '$lookup': {
                    'from': 'publication_filled',
                    'localField': 'publicationList.publication_id',
                    'foreignField': 'id',
                    'as': 'publicationList'
                }
            }
        ]))
        client.close()

        # Sort publications by year
        for person in persons:
            if "publicationList" in person and len(person["publicationList"]) > 0:
                person["publicationList"].sort(key=lambda x: x["publYear"], reverse=True)
        return persons

    def remove_persons_without_publications(self):
        """
        Removes all persons without publications.
        :return:
        """
        # Connect to MongoDB
        client = pm.MongoClient(self.MONGODB_TO_URI)
        db = client[self.MONGODB_TO_DB]
        # Remove persons without publications
        db["persons"].delete_many({"publicationList": []})
        client.close()
