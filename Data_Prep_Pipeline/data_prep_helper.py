import os
import pymongo as pm

MONGODB_FROM_URI = os.getenv("MONGODB_FROM_URI",
                             "mongodb://localhost:27017")
MONGODB_FROM_DB = os.getenv("MONGODB_TO_DB", "FLK_Data_Lake")


def get_children_organisation_ids(organisation_id: int):
    """
    Get all children organisation_ids for a given organisation_id
    :param organisation_id: ID of the organisation
    :return: hierarchy of organisation_ids
    """
    organisation_hierarchy = {'id': organisation_id}
    client = pm.MongoClient(MONGODB_FROM_URI)
    db = client[MONGODB_FROM_DB]
    child_organisations = list(db['organisation_organisation'].find({"organisation_id": str(organisation_id)}))
    client.close()
    for child_organisation in child_organisations:
        children_json = get_children_organisation_ids(int(child_organisation["child_organisation_id"]))
        if 'children' not in organisation_hierarchy:
            organisation_hierarchy['children'] = []
        else:
            organisation_hierarchy['children'].append(children_json)

    return organisation_hierarchy


def get_persons_ids_for_organisation(organisation_id: int):
    """
    Get all persons for a given organisation_id
    :param organisation_id: ID of the organisation
    :return: list of person_ids
    """
    client = pm.MongoClient(MONGODB_FROM_URI)
    db = client[MONGODB_FROM_DB]
    person_dicts = list(db['organisation_persons'].find({"organisation_id": str(organisation_id)}))
    client.close()
    person_ids = [int(person_dict['person_id']) for person_dict in person_dicts]
    return person_ids


def get_publications_for_person(person_id):
    """
    Get all publications for a given person_id
    :param person_id: ID of the person
    :return: list of publication_ids
    """
    client = pm.MongoClient(MONGODB_FROM_URI)
    db = client[MONGODB_FROM_DB]
    publication_dicts = list(db['person_publications'].find({"person_id": str(person_id)}))
    client.close()
    publication_ids = [int(publication_dict['publication_id']) for publication_dict in publication_dicts]
    return publication_ids


def get_publication_ids_for_organisation(organisation_id: int):
    """
    Get all publications for a given organisation_id
    :param organisation_id:
    :return: list of publication_ids
    """
    client = pm.MongoClient(MONGODB_FROM_URI)
    db = client[MONGODB_FROM_DB]
    publication_dicts = list(db['organisation_publications'].find({"organisation_id": str(organisation_id)}))
    client.close()
    publication_ids = [int(publication_dict['publication_id']) for publication_dict in publication_dicts]
    return publication_ids


def get_wi_ids():
    """
    Get the ids from the mongo collection "publication" that are published by the Department of Information Systems
    :return:
    """
    wi_ids = []

    for organisation in get_children_organisation_ids(31923392)['children']:
        organisation_id = int(organisation['id'])
        publications = get_publication_ids_for_organisation(organisation_id)
        wi_ids.extend(publications)
    wi_ids = list(set(wi_ids))
    wi_ids = [str(x) for x in wi_ids]
    return wi_ids

def get_wi_persons():
    """
    Get the ids from the mongo collection "person" that are published by the Department of Information Systems
    :return:
    """
    wi_ids = []
    for organisation in get_children_organisation_ids(31923392)['children']:
        organisation_id = int(organisation['id'])
        person_ids = get_persons_ids_for_organisation(organisation_id)
        wi_ids.extend(person_ids)

    return wi_ids


