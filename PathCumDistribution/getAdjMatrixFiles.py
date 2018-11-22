import networkx as nx

# Open adjencency list file and build the undirected graph
f = open("../lightningAdjList.txt", 'rb')
G = nx.read_multiline_adjlist(f, create_using=nx.Graph)
f.close()

# Get number of edges and nodes
print("Number of nodes: " + str(G.number_of_nodes()))
print("Number of edges: " + str(G.number_of_edges()))

# Iterate through different graphs, in each iteration we exclude
# edges with capacity less than x, x increases by tenfold in each iteration
for i in range(0, 7):

    # Get a fresh copy of the graph
    newG = G.copy()

    capacityThreshold = 10**i
    edgesToRemove = []

    # Remove edges we don't need
    for e in newG.edges():
        if int(newG[e[0]][e[1]]['capacity']) < capacityThreshold:
            print(int(newG[e[0]][e[1]]['capacity']))
            edgesToRemove.append((e[0], e[1]))

    newG.remove_edges_from(edgesToRemove)

    # Get the adj matrix
    a = nx.to_numpy_matrix(G)
    rows = a.shape[0]
    cols = a.shape[1]

    f = open("adjMatrix" + str(capacityThreshold) + ".txt", "w")

    # Write the adj matrix in the file
    for x in range(0, rows):
        if x != 0:
            f.write("\n")
        for y in range(0, cols):
            if(y != cols - 1):
                f.write(str(int(a[x, y])) + "\t")
            else:
                f.write(str(int(a[x, y])))

    f.close()
