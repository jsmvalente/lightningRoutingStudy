import networkx as nx

class ShortestPathRouting:

    def __init__(self, G):

        self.G = G

        return

    def simulatePayment(self, source, destination, amount):

        # Find shortest path between source and destination
        shortest_path = nx.shortest_path(self.G, source, destination)

        # Find if the payment can go through
        validPath = True
        for i in range(0, len(shortest_path) - 2):

            node1 = shortest_path[i]
            node2 = shortest_path[i + 1]

            # If one of the channels has not enough capacity the path is not valid
            if self.G[node1][node2][node1] < amount:
                return False


        # Change the state of the channels in the path
        for i in range(0, len(shortest_path) - 2):
            node1 = shortest_path[i]
            node2 = shortest_path[i + 1]

            self.G[node1][node2][node1] -= amount
            self.G[node1][node2][node2] += amount

        return True

