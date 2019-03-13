import networkx as nx
import random
import numpy as np
import routing

# Open adjencency list file and build the undirected graph
f = open("adjList.txt", 'rb')
G = nx.read_multiline_adjlist(f)
f.close()

# Clean graph from smallest components
G = max(nx.connected_component_subgraphs(G), key=len)

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

f.close()


# Create channel state balances
for e in G.edges:
    capacity = G[e[0]][e[1]]["capacity"]
    balance = capacity/2
    # Create two dic entries with the ids of the nodes and their balances in the channel
    G[e[0]][e[1]][e[0]] = balance
    G[e[0]][e[1]][e[1]] = balance


# Simulate with n payments between two nodes
nodes = list(G.nodes)
nPayments = 500

print("Trying " + str(nPayments) + " payments")

# Use gaussian probability distribution for random payment amounts

# mean and standard deviation
mu, sigma = 250000, 6000
paymentAmounts = np.random.normal(mu, sigma, nPayments).tolist()
Gcopy = G.copy()
sourceDestination = []
paymentShortestPathCount = 0
paymentRoutingCount = 0

# Find source and destination nodes
for _ in range(0, nPayments):
    # Choose a random source
    source = nodes[random.randint(0, len(nodes) - 1)]

    # Choose a random destination thats different from the source
    while True:
        dest = nodes[random.randint(0, len(nodes) - 1)]
        if dest != source:
            break

    sourceDestination += [(source, dest)]

# Run shortest path until there are no more (source, destination)
for i in range(0, nPayments):

    # Find shortest path between source and destination
    shortest_path = nx.shortest_path(G, sourceDestination[i][0], sourceDestination[i][1])

    # Find if the payment can go through
    for i in range(0, len(shortest_path) - 2):

        node1 = shortest_path[i]
        node2 = shortest_path[i+1]

        if G[node1][node2][node1] > paymentAmounts[0]:

            # Change the state of the channels in the path
            paymentShortestPathCount += 1

            amount = paymentAmounts[i]

            for i in range(0, len(shortest_path) - 2):
                node1 = shortest_path[i]
                node2 = shortest_path[i + 1]

                G[node1][node2][node1] -= amount
                G[node1][node2][node2] += amount
                break

print("Shortest Path Success: " + str(paymentShortestPathCount))

# Run routing until there are no more (source, destination) pairs
routing = routing.Routing(Gcopy)
for i in range(0, nPayments):

    if routing.newPayment(Gcopy, sourceDestination[i][0], sourceDestination[i][1], paymentAmounts[i]):
        paymentRoutingCount += 1

print("Routing Success: " + str(paymentRoutingCount))
