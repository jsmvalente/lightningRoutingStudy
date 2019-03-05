import networkx as nx
import random
import numpy as np

# Open adjencency list file and build the directed graph
f = open("../scripts/lightningAdjList.txt", 'rb')
G = nx.read_multiline_adjlist(f)
f.close()

# Clean graph from smallest components
G = max(nx.connected_component_subgraphs(G), key=len)

print("Number of nodes: " + str(G.number_of_nodes()))
print("Number of edges: " + str(G.number_of_edges()))

# Check if capacity is correct
n1 = "02c91d6aa51aa940608b497b6beebcb1aec05be3c47704b682b3889424679ca490"
n2 = "0311cad0edf4ac67298805cf4407d94358ca60cd44f2e360856f3b1c088bcd4782"
print(G[n1][n2])

# Read alias file and create a pub_key -> alias dic
aliasDic = {}
f = open("../scripts/nodeAlias.txt", 'r')

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

# Use gaussian probability distribution for random payment amounts
# mean and standard deviation
mu, sigma = 250001, 6000
paymentAmounts = np.random.normal(mu, sigma, nPayments).tolist()
paymentTryCount = 0
paymentSuccessCount = 0

# Run until there are no more payments to send
while paymentAmounts:

    paymentTryCount += 1

    # Choose a random source
    source = nodes[random.randint(0, len(nodes) - 1)]

    # Choose a random destination
    while True:
        dest = nodes[random.randint(0, len(nodes) - 1)]
        if dest != source:
            break

    # Find shortest path between source and destination
    shortest_path = nx.shortest_path(G, source, dest)

    # Find if the payment can go through
    enoughCapacity = True
    for i in range(0, len(shortest_path) - 2):

        node1 = shortest_path[i]
        node2 = shortest_path[i+1]

        if G[node1][node2][node1] < paymentAmounts[0]:
            enoughCapacity = False
            break

    # Change the state of the channels in the path
    if enoughCapacity:

        paymentSuccessCount += 1

        amount = paymentAmounts.pop(0)

        for i in range(0, len(shortest_path) - 2):

            node1 = shortest_path[i]
            node2 = shortest_path[i + 1]

            G[node1][node2][node1] -= amount
            G[node1][node2][node2] += amount


print("Count: " + str(paymentTryCount))
print("Success: " + str(paymentSuccessCount))
