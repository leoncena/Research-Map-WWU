import pymongo as pm
import os
import data_prep_helper as helper
from datetime import datetime

MONGODB_TO_URI = os.getenv("MONGODB_TO_URI",
                           "mongodb://localhost:27017")
MONGODB_TO_DB = os.getenv("MONGODB_TO_DB", "FLK_Web")
MONGODB_FROM_URI = os.getenv("MONGODB_FROM_URI",
                             "mongodb://localhost:27017")
MONGODB_FROM_DB = os.getenv("MONGODB_TO_DB", "FLK_Data_Lake")



def generate_org_json(organisation_id: int):
    """
    Generate a json for a given organisation_id
    :param organisation_id: ID of the organisation
    :return: hierarchy of all organisations and persons and publications sorted by year
    """
    client = pm.MongoClient(MONGODB_FROM_URI)
    db = client[MONGODB_FROM_DB]
    organisation = db['organisation'].find_one({"id": str(organisation_id)})
    client.close()
    organisation_json = {'id': str(organisation_id), 'name': organisation['cfName'], 'children': []}
    print("Generate JSON for Organisation: " + str(organisation_json['name']))
    for person_id in helper.get_persons_ids_for_organisation(organisation_id):
        person_json = generate_person_json(person_id)
        if not person_json:
            continue
        organisation_json['children'].append(person_json)
    return organisation_json


def generate_person_json(person_id: int):
    """
    Generate a json for a given person_id
    :param person_id: ID of the person
    :return: json of the person with all publications sorted by year
    """
    client = pm.MongoClient(MONGODB_FROM_URI)
    db = client[MONGODB_FROM_DB]
    person = db['person'].find_one({"id": str(person_id)})
    if not person:
        return {}
    person_json = {'name': get_full_name(person_id), 'id': str(person_id), 'children': []}
    publication_ids = helper.get_publications_for_person(person_id)
    publication_list = generate_publication_json(publication_ids)
    if not publication_list:
        return {}
    person_json['children'] = publication_list
    return person_json


def generate_publication_json(publication_ids: list):
    """
    Generate a json for a given publication_id
    :param publication_ids: ID of the publication
    :return: list of publications sorted by year hierarchically
    """

    client = pm.MongoClient(MONGODB_FROM_URI)
    db = client[MONGODB_FROM_DB]
    publication_ids = [str(publication_id) for publication_id in publication_ids]
    publications = db['publication'].aggregate(
        [
            {
                '$match': {
                    'id': {
                        '$in': publication_ids
                    },
                    'publYear': {
                        '$gt': datetime.now().year - 3
                    }
                }
            },
            {
                '$group': {
                    '_id': '$publYear',
                    'children': {
                        '$push': '$$ROOT'
                    }
                }
            }
        ]
    )
    publications = list(publications)
    client.close()

    publication_list = []
    for year in publications:
        year_json = {'name': str(year['_id']), 'children': []}
        for publication in year['children']:
            publication_json = {'id': publication['id'], 'name': publication['cfTitle'], 'loc': 1}
            year_json['children'].append(publication_json)
        publication_list.append(year_json)
    return publication_list


def get_full_name(person_id: int):
    """
    Get full name of a person including title
    :param person_id: ID of the person
    :return: full name
    """
    client = pm.MongoClient(MONGODB_FROM_URI)
    db = client[MONGODB_FROM_DB]
    person = db['person'].find_one({"id": str(person_id)})
    client.close()
    academic_title = person['academicTitle'] if person['academicTitle'] is not None else ''
    first_name = person['cfFirstNames'] if person['cfFirstNames'] is not None else ''
    family_name = person['cfFamilyNames'] if person['cfFamilyNames'] is not None else ''
    person_name = academic_title + " " + first_name + " " + family_name
    return person_name


def generate_sunburst_json():
    """
    Generate a json for the sunburst
    :return: None
    """
    sunburst_list = []
    for organisation in helper.get_children_organisation_ids(31923392)['children']:
        generated_org_json = generate_org_json(organisation['id'])
        if generated_org_json:
            sunburst_list.append(generated_org_json)

    mongodb_instance = pm.MongoClient(MONGODB_TO_URI)
    to_db = mongodb_instance[MONGODB_TO_DB]
    to_db['inst_wi_hrchy'].delete_many({})
    to_db['inst_wi_hrchy'].insert_one({'children': sunburst_list})
    mongodb_instance.close()
