import networkx as nx
import matplotlib.pyplot as plt
import distributedrouting
import shortestpathrouting
import statistics
import payment as pmt
import random

# Number of simulation runs
nSimulation = 1
# Number of payments in each simulation run
nPayments = 200
# Payments gaussian mean weight to be multiplied by average channel balance
payments_mu_weight = 0.1
# Payemnts gaussian standard deviation
payments_sigma_weight = payments_mu_weight/2
# Number of nodes to have before stopping removing nodes
nNodes = 280
# Number of routing gossip messages to be sent in-between payments
nRoutingGossip = 10

# Open adjencency list file and build the undirected graph
f = open("adjList.txt", 'rb')
G = nx.read_multiline_adjlist(f)
f.close()

# Clean graph from smallest components
largest_cc = max(nx.connected_components(G), key=len)
cleanG = G.subgraph(largest_cc).copy()

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

# Variables to accumulate the studid values
shortestPathSuccessAcumm = 0
shortestPathAPLAcumm = 0
shortestPathOvercapAcumm = 0
shortestPathNonExisAcumm = 0
distRoutingSuccessAcumm = 0
distRoutingAPLAcumm = 0
distRoutingOvercapAcumm = 0
distRoutingNonExisAcumm = 0

for i in range(nSimulation):

    # Remove a fraction of the nodes so the network is easier to analyze
    # Since we are working with a scale-free network robustness to random node removals is expected
    G = cleanG.copy()
    
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

    # # Reduce number of labels to half so they're easier to visualize
    # nodes = list(G.nodes)
    # random.shuffle(nodes)
    # labelDic = dict(zip(nodes, nodes))
    # for i in range(0, int(len(nodes)/1.5)):
    #     labelDic[nodes[i]] = ""

    # # Visualize graph
    # nx.draw(G, with_labels=True, labels=labelDic, font_size=10, label="Leftover LN", node_color='#00b4d9', edge_color="gray")
    # plt.show()

    # Create channel state balances
    balances = []
    for e in G.edges:
        capacity = G[e[0]][e[1]]["capacity"]
        balance = capacity/2
        balances.append(balance)
        # Create two dic entries with the ids of the nodes and their balances in the channel
        G[e[0]][e[1]][e[0]] = balance
        G[e[0]][e[1]][e[1]] = balance

    # Get the payment distribution mu and sigma from the average node capacity
    medianBalance = statistics.median(balances)
    payments_mu = medianBalance*payments_mu_weight
    payments_sigma = medianBalance*payments_sigma_weight

    # Simulate with n payments between two nodes
    payments = pmt.createPayments(nPayments, nodes, payments_mu, payments_sigma)
    print("Simulating " + str(nPayments) + " payments")

    # Get a copy of G to be used in the each routing scheme
    Gcopy_shortPath = G.copy()
    Gcopy_dist = G.copy()

    # Init routing schemes
    shortPathRouting = shortestpathrouting.ShortestPathRouting(Gcopy_shortPath)
    distRouting = distributedrouting.DistributedRouting(Gcopy_dist, nRoutingGossip)

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
    shortestPathSuccess = 0
    shortestPathAPL = 0
    shortestPathOvercap = 0
    shortestPathNonExis = 0
    distRoutingSuccess = 0
    distRoutingAPL = 0
    distRoutingOvercap = 0
    distRoutingNonExis = 0

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
            print("Distributed Routing overcap and shortest path success")


    # Draw the channel balance distribution
    # plt.hist(balances, bins = 10)
    # plt.ylabel("Frequency")
    # plt.xlabel("Balance (Satoshis)")
    # plt.show()

    # Print this runs stats
    print("\nMedian Channel Balance: " + str(medianBalance) + "\n" +
            "Number Of Payments: " + str(nPayments) + "\n" + 
            "Payments µ: " + str(payments_mu) + "\n" +
            "Payments σ: " + str(payments_sigma) + "\n")
    
    shortestPathSuccess = round((shortPathRoutingCount/nPayments)*100, 2)
    shortestPathSuccessAcumm += shortestPathSuccess
    shortestPathAPL = round(shortPathCumlLen / shortPathRoutingCount, 2)
    shortestPathAPLAcumm += shortestPathAPL
    print("Shortest Path Routing:\n" +
        "P(Success) = " + str(shortestPathSuccess) + "%\n" +
        "Average path length = " + str(shortestPathAPL))
    if nPayments != shortPathRoutingCount:
        shortestPathOvercap = round((shortPathOverCap / (nPayments-shortPathRoutingCount)) * 100, 2)
        shortestPathNonExis = round((shortPathNonExis / (nPayments-shortPathRoutingCount)) * 100, 2)
        shortestPathOvercapAcumm += shortestPathOvercap
        shortestPathNonExisAcumm += shortestPathNonExis
        print("P(Overcap|Failed) = " + str(shortestPathOvercap) + "%\n" +
        "P(NonExis|Failed) = " + str(shortestPathNonExis) + "%")

    distRoutingSuccess = round((distRoutingCount / nPayments) * 100, 2)
    distRoutingSuccessAcumm += distRoutingSuccess
    print("\nDistributed Routing:\n" +
        "P(Success) = " + str(distRoutingSuccess) + "%")
    if distRoutingCount:
        distRoutingAPL = round(distPathCumlLen / distRoutingCount, 2)
        distRoutingAPLAcumm += distRoutingAPL
        print("Average path length = " + str(distRoutingAPL))
    if nPayments != distRoutingCount:
        distRoutingOvercap = round((distRoutingOverCap / (nPayments - distRoutingCount)) * 100, 2)
        distRoutingNonExis = round((distRoutingNonExis / (nPayments - distRoutingCount)) * 100, 2)
        distRoutingOvercapAcumm += distRoutingOvercap
        distRoutingNonExisAcumm += distRoutingNonExis
        print("P(Overcap|Failed) = " + str(distRoutingOvercap) + "%\n" +
        "P(NonExis|Failed) = " + str(distRoutingNonExis) + "%")


# Print the final stats
print("\n\nResults from " + str(nSimulation) + " simulation runs.\n")
print("Average Shortest Path Routing:\n" +
        "P(Success) = " + str(round(shortestPathSuccessAcumm/nSimulation, 2)) + "%\n" +
        "Average path length = " + str(round(shortestPathAPLAcumm/nSimulation, 2)) + "\n" +
        "P(Overcap|Failed) = " + str(round(shortestPathOvercapAcumm/nSimulation, 2)) + "%\n" +
        "P(NonExis|Failed) = " + str(round(shortestPathNonExisAcumm/nSimulation, 2)) + "%")

print("\nAverage Distributed Routing:\n" +
        "P(Success) = " + str(round(distRoutingSuccessAcumm/nSimulation, 2)) + "%\n" +
        "Average path length = " + str(round(distRoutingAPLAcumm/nSimulation, 2)) + "\n" +
        "P(Overcap|Failed) = " + str(round(distRoutingOvercapAcumm/nSimulation, 2)) + "%\n" +
        "P(NonExis|Failed) = " + str(round(distRoutingNonExisAcumm/nSimulation, 2)) + "%")

print("\nAverage Delta = " + str(round( (distRoutingSuccessAcumm-shortestPathSuccessAcumm) / nSimulation, 2)))