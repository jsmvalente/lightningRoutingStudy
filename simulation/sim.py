import networkx as nx
import distributedrouting
import shortestpathrouting
import payment

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
payments = payment.createPayments(500, nodes)
print("Trying " + str(nPayments) + " payments")

# Get a copy of G to be used in the second routing scheme
Gcopy = G.copy()

# Init routing schemes
shortPathRouting = shortestpathrouting.ShortestPathRouting(G)
distRouting = distributedrouting.DistributedRouting(Gcopy)

# Simulate payments
shortPathRoutingCount = 0
distRoutingCount = 0
for payment in payments:
    print(str(payment.amount))
    if shortPathRouting.simulatePayment(payment.source, payment.destination, payment.amount):
        shortPathRoutingCount += 1

    if distRouting.simulatePayment(payment.source, payment.destination, payment.amount):
        distRoutingCount += 1


print("Shortest Path Routing had a " + str(shortPathRoutingCount/nPayments) + "% of success")
print("Distributed Routing had a " + str(distRoutingCount/nPayments) + "% of success")