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

plt.rc("savefig", dpi=1000)

MONGODB_TO_URI = os.getenv('PIPELINE_ENV_MONGODB_TO_URI',
                           "mongodb://localhost:27017")
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
df = df[["id", 'cfTitle', 'cfAbstr', 'keywords', "title_nlp", "abstract_nlp", "keywords_nlp"]]
len1 = len(df)
# only use the entries that have a title, abstarct and keywords
df = df[df['cfTitle'].notna() & df['cfAbstr'].notna() & df['keywords'].notna()]
len2 = len(df)
len3 = len1 - len2
print("articles that didnt have title, abstract and keywords")
print(len3)

# create a vectorization function using the universal sentence encoder
module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
model = hub.load(module_url)


def embed(input):
    return model(input)


# calculate the adjacency matrix
def adj_mat(pubs):
    # vectorize the abstracts
    vectors = embed(pubs.loc[:, "abstract_nlp"])
    # use the inner product as similarity
    mat = np.inner(vectors, vectors)
    # normalize the values between 0 and 1
    mat = (mat - np.min(mat)) / (np.max(mat) - np.min(mat))
    np.fill_diagonal(mat, 0)
    return mat


adjacencymatrix = adj_mat(df)
# creating a networkx graph out of the combinationmatrix
graph = nx.from_numpy_array(adjacencymatrix)
# add labels to the nodes
graph = nx.relabel_nodes(graph, dict(zip(graph, df["id"])))

# delete weak links
q = np.quantile(adjacencymatrix, .99)
mk.dropEdges(graph, minWeight=q)
print("graph stats after deleting weak links")
print(mk.graphStats(graph))
# use only the largest connected subgraph
graph = max((graph.subgraph(c) for c in nx.connected_components(graph)), key=len)
print("graph stats after selecting largest subgraph")
print(mk.graphStats(graph))
len4 = len(graph.nodes)
len5 = len2 - len4
print("articles that were deleted for clarity")
print(len5)
len6 = len1 - len4
print("absolute amount of articles not displayed")
print(len6)

# add clusters
partition = community.best_partition(graph)
colors = [partition[n] for n in graph.nodes()]
my_colors = plt.cm.Set2

# draw the graph
nx.draw_spring(graph, node_size=1, node_color=colors, cmap=my_colors, with_labels=True, font_size=1,
               edge_color="#D4D5CE", alpha=.95, width=0.1)
# plt.savefig('figures/pub_net.png')


# returns the list of all nodes for the json file
def getNodes():
    nodes = []
    for name, group in partition.items():
        node = {"id": name, "group": group}
        nodes.append(node)
    return nodes


# returns a list of all links for the json file
def getLinks():
    links = []
    for edge in graph.edges.data():
        link = {"source": edge[0], "target": edge[1], "value": edge[2]["weight"]}
        links.append(link)
    return links


# saves the greph in a json file
jsonGraph = {"nodes": getNodes(), "links": getLinks()}
# jsonString = json.dumps(jsonGraph)
# jsonFile = open("data/pub_net_graph.json", "w")
# jsonFile.write(jsonString)
# jsonFile.close()


# save in the mongodb
MONGODB_TO_DB = "FLK_Web"
mongo_client = pm.MongoClient(MONGODB_TO_URI)
to_db = mongo_client[MONGODB_TO_DB]
network = to_db["network"]
network.delete_many({})
network.insert_one(jsonGraph)
