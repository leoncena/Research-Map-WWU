import os
import pymongo as pm
import pandas as pd
import numpy as np
import tensorflow_hub as hub
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
import networkx as nx
import metaknowledge as mk
import community                # pip install python-louvain
import json
import matplotlib.pyplot as plt

plt.rc("savefig", dpi=1000)

def get_keywords():
    MONGODB_TO_URI = os.getenv('PIPELINE_ENV_MONGODB_TO_URI',"mongodb://localhost:27017/")
    # get the data from the mogodb
    MONGODB_FROM_DB = "FLK_Data_Lake"
    mongo_client = pm.MongoClient(MONGODB_TO_URI)
    from_db = mongo_client[MONGODB_FROM_DB]
    publications = from_db["publication_filled"]
    pubs = publications.find({})

    # put the data in a dataframe
    pubs_list = list(pubs)
    df = pd.DataFrame(pubs_list)

    # get rid of some columns
    df = df[["id",'cfTitle', 'keywords',"title_nlp", "keywords_nlp"]]
    len1 = len(df)
    # only use the entries that have a title and keywords
    df = df[df['cfTitle'].notna() & df['keywords'].notna()]
    len2 = len(df)
    len3 = len1 - len2
    print("articles that didnt have title and keywords")
    print(len3)

    keywords = list(df.loc[:,"keywords_nlp"])
    keywords = list(filter(lambda item: isinstance(item, list), keywords))
    keywords = sum(keywords, [])
    # lemmatize
    lemma = nltk.wordnet.WordNetLemmatizer()
    lemmatized = []
    for i in keywords:
        lemmatized.append(lemma.lemmatize(i))
    # only unique keywords
    keywords_unique = list(set(lemmatized))
    return keywords_unique

def create_model():
    # create a vectorization function using the universal sentence encoder
    module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
    global model
    model = hub.load(module_url)

def embed(input):
  return model(input)

# calculate the adjacency matrix
def adj_mat(keywords):
    # vectorize the keywords
    vectors = embed(keywords)
    # use the inner product as similarity
    mat = np.inner(vectors, vectors)
    # normalize the values between 0 and 1
    mat = (mat-np.min(mat))/(np.max(mat)-np.min(mat))
    np.fill_diagonal(mat, 0)
    return mat

def calc_graph(keywords_unique):
    adjacencymatrix = adj_mat(keywords_unique)
    # creating a networkx graph out of the combinationmatrix
    graph = nx.from_numpy_array(adjacencymatrix)
    # add labels to the nodes
    graph = nx.relabel_nodes(graph, dict(zip(graph, keywords_unique)))

    # delete weak links
    len4 = len(graph.nodes)
    q = np.quantile(adjacencymatrix, .9995)
    mk.dropEdges(graph, minWeight = q)
    print("graph stats after deleting weak links")
    print(mk.graphStats(graph))
    # use only the largest connected subgraph
    graph = max((graph.subgraph(c) for c in nx.connected_components(graph)), key=len)
    print("graph stats after selecting largest subgraph")
    print(mk.graphStats(graph))
    len5 = len(graph.nodes)
    len6 = len4 - len5
    print("keywords that were deleted for clarity")
    print(len6)

    # add clusters
    partition = community.best_partition(graph)

    return graph, partition

# returns the list of all nodes for the json file
def getNodes(partition):
    nodes = []
    for name, group in partition.items():
        node = {"id": name, "group": group}
        nodes.append(node)
    return nodes

# returns a list of all links for the json file
def getLinks(graph):
    links = []
    for edge in graph.edges.data():
        link = {"source": edge[0], "target": edge[1], "value": edge[2]["weight"]}
        links.append(link)
    return links

def save_graph(graph, partition):
    # creates a json file for the graph
    jsonGraph = {"nodes":getNodes(partition), "links":getLinks(graph)}

    # save in the mongodb
    MONGODB_TO_URI = os.getenv('PIPELINE_ENV_MONGODB_TO_URI',
                            "mongodb://localhost:27017/")
    MONGODB_TO_DB = "FLK_Web"
    mongo_client = pm.MongoClient(MONGODB_TO_URI)
    to_db = mongo_client[MONGODB_TO_DB]
    network = to_db["network"]
    if "network" in to_db.list_collection_names():
        network.delete_many({})
    network.insert_one(jsonGraph)

def run_key_net():
    keywords = get_keywords()
    create_model()
    graph, partition = calc_graph(keywords)
    save_graph(graph, partition)
