import networkx as nx

class ShortestPathRouting:

    def __init__(self, G):

        self.G = G

        return

    # Simulate the payment and change the channel states accordingly. If the path is not valid return -2. If the payment
    # was successful then return 0
    def simulatePayment(self, source, destination, amount):

        # Find shortest path between source and destination
        shortest_path = nx.shortest_path(self.G, source, destination)

        # Find if the payment can go through
        for i in range(0, len(shortest_path) - 1):

            node1 = shortest_path[i]
            node2 = shortest_path[i + 1]

            # If one of the channels has not enough capacity the path is not valid
            if self.G[node1][node2][node1] < amount:
                # If there isn't enough capacity on a path channel return -2
                # print("Shortest Path Routing: Invalid path. Not enough balance on: " + node1 + " -> " + node2)
                return -2

        # Change the state of the channels in the path
        for i in range(0, len(shortest_path) - 1):
            node1 = shortest_path[i]
            node2 = shortest_path[i + 1]

            self.G[node1][node2][node1] -= amount
            self.G[node1][node2][node2] += amount

        return len(shortest_path)

