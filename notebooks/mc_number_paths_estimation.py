#!/usr/bin/env python

import networkx as nx
import numpy as np

def init_adjacency(G):
    A = np.zeros((G.number_of_nodes(), G.number_of_nodes()))

    edges = nx.adjacency_matrix(G)

    nodes = list(G.nodes())


    for n in nodes:
        for neigh in G.neighbors(n):
            A[nodes.index(n)][nodes.index(neigh)] = 1
    return A



# In[ ]:





# In[ ]:

def estimate_number_paths_node(G, node, iterations=1000):
    paths = []
    dist = {}

    nodes = list(G.nodes())
    
    for it in range(iterations):
        A = init_adjacency(G)
        
        x_t = 0
        c = 0
        g = 1
        t = 1

        V = []
        for neigh in G.neighbors(nodes[x_t]):
            V += [nodes.index(neigh)]

        n = len(V)




        for i in range(len(A[x_t])):
            A[i][0] = 0
        
        path = [x_t]

        while(1):
            if(not x_t == 0):
                V = []
                for neigh in G.neighbors(nodes[x_t]):
                    if(not A[x_t][nodes.index(neigh)]):
                        continue
                    V += [nodes.index(neigh)]

            if(len(V) == 0):
                break

            x_t1 = np.random.choice(V)

            x_t = x_t1
            c = x_t1
            path += [x_t]
            g = g/len(V)
            for i in range(len(A[x_t1])):
                A[i][x_t] = 0

            t = t + 1

            if(c == n):
                break

        
        paths += [path]
        dist[tuple(path)] = g

        
    return dist


