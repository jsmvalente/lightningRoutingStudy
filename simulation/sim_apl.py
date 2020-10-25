import networkx as nx
import matplotlib.pyplot as plt
import distributedrouting
import shortestpathrouting
import statistics
import payment as pmt
import random

nPaths = 10000
aplAcumm = 0

# Open adjencency list file and build the undirected graph
f = open("adjList.txt", 'rb')
G = nx.read_multiline_adjlist(f)
f.close()

print("Number of nodes: " + str(G.number_of_nodes()))
print("Number of edges: " + str(G.number_of_edges()))

# Read alias file and create a pub_key -> alias dic
aliasDic = {}
f = open("nodeAlias.txt", 'r')

lines = f.read().splitlines()

for line in lines:
    pub_key = line[:66]
    alias = line[67:]
    aliasDic[pub_key] = alias

nodes = list(G.nodes)

# Find source and destination nodes
for i in range(0, nPaths):
    # Choose a random source
    source = nodes[random.randint(0, len(nodes) - 1)]
    #Choose a random destination
    destination = nodes[random.randint(0, len(nodes) - 1)]

    #Skip if they are the same
    if source == destination:
        i-=1
        continue

    # Find shortest path between source and destination
    try:
        shortest_path = nx.shortest_path(G, source, destination)
    #Skip if there's an error
    except:
        i-=1
        continue

    #Add the size of the path to the accumulation variable
    aplAcumm += len(shortest_path)

print("APL = " + str(aplAcumm/nPaths))