import networkx as nx
import numpy as np
import time
# Open adjencency list file and build the undirected graph
f = open("../lightningAdjList.txt", 'rb')
G = nx.read_multiline_adjlist(f, create_using=nx.Graph)
f.close()


print("Number of nodes: " + str(G.number_of_nodes()))
print("Number of edges: " + str(G.number_of_edges()))

dicG = nx.to_dict_of_dicts(G)

print(len(dicG))

f = open("adjList.txt", "w")

# for key, value in dicG.items():
#     f.write("+" + key + "\n")
#     for adjKey, _ in value.items():
#         f.write(adjKey + "\n")

a = nx.to_numpy_matrix(G)
rows = a.shape[0]
cols = a.shape[1]

print(a[0, 0])
print(a[0, 1])

for x in range(0, rows):
    if x != 0:
        f.write("\n")
    for y in range(0, cols):
        f.write(str(int(a[x, y])) + "\t")

f.close()
