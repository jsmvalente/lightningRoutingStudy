import networkx as nx
import matplotlib.pyplot as plt
import distributedrouting
import shortestpathrouting
import payment
import random

nPayments = 300
nNodes = 200

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
plt.show()
# Remove a fraction of the nodes so the network is easier to analyze
# Since we are working with a scale-free network robustness to random node removals is expected

# Remove nodes until there are only nNodes
while G.number_of_nodes() > nNodes:
    # Choose node to remove
    randomNode = random.choice(list(G.nodes))
    G.remove_node(randomNode)

# Clean graph from smallest components
print("Node removal broke graph into " + str(nx.number_connected_components(G)) + " connected components.")
G = max(nx.connected_component_subgraphs(G), key=len)
print("Biggest component has " + str(G.number_of_nodes()) + " nodes.")

# Visualize graph
nx.draw(G, with_labels=True, font_size=6, label="Leftover LN")
plt.show()

# Create channel state balances
for e in G.edges:
    capacity = G[e[0]][e[1]]["capacity"]
    balance = capacity/2
    # Create two dic entries with the ids of the nodes and their balances in the channel
    G[e[0]][e[1]][e[0]] = balance
    G[e[0]][e[1]][e[1]] = balance


# Simulate with n payments between two nodes
nodes = list(G.nodes)
payments = payment.createPayments(nPayments, nodes)
print("Trying " + str(nPayments) + " payments")

# Get a copy of G to be used in the second routing scheme
Gcopy = G.copy()

# Init routing schemes
shortPathRouting = shortestpathrouting.ShortestPathRouting(G)
distRouting = distributedrouting.DistributedRouting(Gcopy)

# Simulate payments
result = 0
shortPathRoutingCount = 0
shortPathOverCap = 0
shortPathNonExis = 0
shortPathCumlLen = 0
distRoutingCount = 0
distRoutingOverCap = 0
distRoutingNonExis = 0
distPathCumlLen = 0

for payment in payments:
    # Simulate the payment using shortest path routing
    result = shortPathRouting.simulatePayment(payment.source, payment.destination, payment.amount)

    if result == -1:
        shortPathNonExis += 1
    elif result == -2:
        shortPathOverCap += 1
    else:
        shortPathCumlLen += result
        shortPathRoutingCount += 1

    # Simulate the payment using distributed routing
    result = distRouting.simulatePayment(payment.source, payment.destination, payment.amount)

    if result == -1:
        distRoutingNonExis += 1
    elif result == -2:
        distRoutingOverCap += 1
    else:
        distPathCumlLen += result
        distRoutingCount += 1

print("Shortest Path Routing:\n" +
      "P(Success) = " + str(round((shortPathRoutingCount/nPayments)*100, 2)) + "%\n" +
      "P(Overcap|Failed) = " + str(round((shortPathOverCap / (nPayments-shortPathRoutingCount)) * 100, 2)) + "%\n" +
      "P(NonExis|Failed) = " + str(round((shortPathNonExis / (nPayments-shortPathRoutingCount)) * 100, 2)) + "%\n" +
      "Average path length = " + str(round(shortPathCumlLen / shortPathRoutingCount, 2)) +
      "\n\nDistributed Routing:\n" +
      "P(Success) = " + str(round((distRoutingCount / nPayments) * 100, 2)) + "%\n" +
      "P(Overcap|Failed) = " + str(round((distRoutingOverCap / (nPayments - distRoutingCount)) * 100, 2)) + "%\n" +
      "P(NonExis|Failed) = " + str(round((distRoutingNonExis / (nPayments - distRoutingCount)) * 100, 2)) + "%")

if distRoutingCount:
    print("Average path length = " + str(round(distPathCumlLen / distRoutingCount, 2)))
