import networkx as nx
import numpy as np
import time
# Open adjencency list file and build the undirected graph
f = open("../lightningAdjList.txt", 'rb')
G = nx.read_multiline_adjlist(f, create_using=nx.Graph)
f.close()

print("Number of nodes: " + str(G.number_of_nodes()))
print("Number of edges: " + str(G.number_of_edges()))

# Read alias file and create a pub_key -> alias dic


# Get the shortest path between all nodes
paths = list(nx.all_pairs_shortest_path(G))
print(paths)
