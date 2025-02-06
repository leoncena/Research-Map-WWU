import os
import pymongo as pm
import pandas as pd
import numpy as np
import tensorflow_hub as hub
import networkx as nx
import metaknowledge as mk
import community
import json
import matplotlib.pyplot as plt
import data_prep_helper as helper

def get_data():
    MONGODB_TO_URI = os.getenv('PIPELINE_ENV_MONGODB_TO_URI',
                           "mongodb://localhost:27017/")

    # get all the publication author connections
    MONGODB_FROM_DB = "FLK_Data_Lake"
    mongo_client = pm.MongoClient(MONGODB_TO_URI)
    from_db = mongo_client[MONGODB_FROM_DB]
    author_publications = from_db["person_publications"]
    auth_pubs = author_publications.find({})

    auth_ids = helper.get_wi_persons()
    auth_ids = [str(i) for i in auth_ids]
    authors = from_db["person"]
    auth = authors.find({"id": {"$in": auth_ids}})

    # put the data in a dataframe
    auth_list = list(auth)
    df1 = pd.DataFrame(auth_list)
    auth_pubs_list = list(auth_pubs)
    df2 = pd.DataFrame(auth_pubs_list)

    # get rid of some columns
    df1 = df1[["id",'cfFamilyNames', 'cfFirstNames']]

    # get rid of some columns
    df2 = df2[["person_id",'publication_id']]

    return df1, df2


# get all the coauthors an author has worked with
def coauth(author, author_pubs, df1):
    pubs = author_pubs.loc[author_pubs["person_id"] == author]
    coauth = author_pubs.loc[author_pubs["publication_id"].isin(list(pubs["publication_id"]))]
    # only use the WI authors
    coauth = coauth.loc[coauth["person_id"].isin(list(df1["id"]))]
    
    return coauth


# calculate the adjacency matrix for one author
def adj_mat(author, coauthors):
    unique_auth = list(set(coauthors["person_id"]))
    unique_pub = set(coauthors["publication_id"])
    adj_mat = pd.DataFrame(columns = unique_auth, index = unique_auth, data = np.zeros((len(unique_auth), len(unique_auth))))
    for i in unique_pub:
        authors = coauthors[coauthors["publication_id"] == i]["person_id"]
        for j in range(len(authors)):
            for k in range(j+1, len(authors)):
                adj_mat[authors.iloc[j]][authors.iloc[k]] = adj_mat[authors.iloc[j]][authors.iloc[k]] + 1
                
    return adj_mat


# get the name for the given author(id)
def getName(author, df1):
    data = df1[df1["id"] == author]
    name = (data["cfFirstNames"] + " " + data["cfFamilyNames"]).iloc[0]
    
    return name


# returns the list of all nodes for the json file
def getNodes(partition, df1):
    nodes = []
    for number, group in partition.items():
        node = {"id": number, "group": group, "name": getName(str(number), df1)}
        nodes.append(node)
    return nodes


# returns a list of all links for the json file
def getLinks(graph):
    links = []
    for edge in graph.edges.data():
        link = {"source": edge[0], "target": edge[1], "value": edge[2]["weight"]}
        links.append(link)
    return links


def run_aut_net():
    # get the data
    df1, df2 = get_data()
    # clear the mongodb
    MONGODB_TO_DB = "FLK_Web"
    MONGODB_TO_URI = os.getenv('PIPELINE_ENV_MONGODB_TO_URI',
                           "mongodb://localhost:27017/")
    mongo_client = pm.MongoClient(MONGODB_TO_URI)
    to_db = mongo_client[MONGODB_TO_DB]
    network = to_db["author_networks"]
    if "author_networks" in to_db.list_collection_names():
        network.delete_many({})
    # get all the authors from WWU
    for i in set(df1["id"]):
        #create graph
        graph = nx.from_pandas_adjacency(adj_mat(i, coauth(i, df2, df1)))
        #add clusters
        partition = community.best_partition(graph)
        #save json
        jsonGraph = {"id":i, "nodes":getNodes(partition, df1), "links":getLinks(graph)}
        #save in the mongodb
        network.insert_one(jsonGraph)
