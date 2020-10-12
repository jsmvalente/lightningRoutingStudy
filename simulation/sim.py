import networkx as nx
import matplotlib.pyplot as plt
import distributedrouting
import shortestpathrouting
import payment
import random

nPayments = 100
# Payments gaussian mean weight to be multiplied by average channel balance
payments_mu_weight = 0.4
# Payemnts gaussian standard deviation
payments_sigma_weight = 0.1
nNodes = 280
#Number of routing gossip messages to be sent in-between payments
nRoutingGossip = 10

# Open adjencency list file and build the undirected graph
f = open("adjList.txt", 'rb')
G = nx.read_multiline_adjlist(f)
f.close()

# Clean graph from smallest components
largest_cc = max(nx.connected_components(G), key=len)
G = G.subgraph(largest_cc).copy()

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
largest_cc = max(nx.connected_components(G), key=len)
G = G.subgraph(largest_cc)
print("Biggest component has " + str(G.number_of_nodes()) + " nodes.")

# Visualize graph
nx.draw(G, with_labels=True, font_size=6, label="Leftover LN")
plt.show()

# Create channel state balances
balanceSum = 0
for e in G.edges:
    capacity = G[e[0]][e[1]]["capacity"]
    balance = capacity/2
    balanceSum += capacity
    # Create two dic entries with the ids of the nodes and their balances in the channel
    G[e[0]][e[1]][e[0]] = balance
    G[e[0]][e[1]][e[1]] = balance

# Get the payment distribution mu and sigma from the average node capacity
averageBalance = balanceSum/(len(G.edges)*2)
payments_mu = averageBalance*payments_mu_weight
payments_sigma = averageBalance*payments_sigma_weight

# Simulate with n payments between two nodes
nodes = list(G.nodes)
payments = payment.createPayments(nPayments, nodes, payments_mu, payments_sigma)
print("Trying " + str(nPayments) + " payments")

# Get a copy of G to be used in the second routing scheme
Gcopy = G.copy()

# Init routing schemes
shortPathRouting = shortestpathrouting.ShortestPathRouting(G)
distRouting = distributedrouting.DistributedRouting(Gcopy, nRoutingGossip)

# Simulate payments
shortPathResult = 0
distPathResult = 0 
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
    shortPathResult = shortPathRouting.simulatePayment(payment.source, payment.destination, payment.amount)

    if shortPathResult == -1:
        shortPathNonExis += 1
    elif shortPathResult == -2:
        shortPathOverCap += 1
    else:
        shortPathCumlLen += shortPathResult
        shortPathRoutingCount += 1

    # Simulate the payment using distributed routing
    distPathResult = distRouting.simulatePayment(payment.source, payment.destination, payment.amount)

    if distPathResult == -1:
        distRoutingNonExis += 1
    elif distPathResult == -2:
        distRoutingOverCap += 1
    else:
        distPathCumlLen += distPathResult
        distRoutingCount += 1

    # Check when the distributed solution fails for overcap and the shortest path finds a path:
    if shortPathResult > 0 and distPathResult == -2:
        print("Distributed ROuting overcap and shortest path success")

print("\nAverage Channel Balance: " + str(averageBalance) + "\n" +
        "Number Of Payments: " + str(nPayments) + "\n" + 
        "Payments µ: " + str(payments_mu) + "\n" +
        "Payments σ: " + str(payments_sigma) + "\n")

print("Shortest Path Routing:\n" +
      "P(Success) = " + str(round((shortPathRoutingCount/nPayments)*100, 2)) + "%\n" +
      "Average path length = " + str(round(shortPathCumlLen / shortPathRoutingCount, 2)))
if nPayments != shortPathRoutingCount:
    print("P(Overcap|Failed) = " + str(round((shortPathOverCap / (nPayments-shortPathRoutingCount)) * 100, 2)) + "%\n" +
      "P(NonExis|Failed) = " + str(round((shortPathNonExis / (nPayments-shortPathRoutingCount)) * 100, 2)) + "%")

print("\nDistributed Routing:\n" +
      "P(Success) = " + str(round((distRoutingCount / nPayments) * 100, 2)) + "%")
if distRoutingCount:
    print("Average path length = " + str(round(distPathCumlLen / distRoutingCount, 2)))
if nPayments != distRoutingCount:
      print("P(Overcap|Failed) = " + str(round((distRoutingOverCap / (nPayments - distRoutingCount)) * 100, 2)) + "%\n" +
      "P(NonExis|Failed) = " + str(round((distRoutingNonExis / (nPayments - distRoutingCount)) * 100, 2)) + "%")