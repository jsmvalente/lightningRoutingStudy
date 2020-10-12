import LNAddresses
import random
import hop
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class DistributedRouting:

    def __init__(self, G, nRoutingGossip):

        self.G = G
        # Number of routing messages to be sent in between payments
        self.nRoutingGossip = nRoutingGossip
        # Routing Tables:
        #   → Node Address:
        #       → Destination:
        #           hop(nextHop, maxCapacity)
        #
        self.routingTables = defaultdict(dict)
        self.addresses = LNAddresses.LNAddresses()
        self.channels = defaultdict(dict)

        # Start by giving each node an LN address
        nodes = list(G.nodes)
        nodeBlocks = []

        # Sort nodes chronologically (timestamp of first seen on blockchain) and give them None addresses
        for node in nodes:

            firstBlock = 999999999
            firstNeighbour = ""
            for neighbour, channelData in G[node].items():

                fundingBlock = channelData["funding_block"]

                if fundingBlock < firstBlock:
                    firstBlock = fundingBlock
                    firstNeighbour = neighbour

            nodeBlocks += [{"node": node, "firstNeighbourNode": firstNeighbour, "firstBlock": firstBlock}]

        # Sort the nodes by their funding transaction order in the blockchain
        def blockSort(data):
            return data["firstBlock"]

        nodeBlocks.sort(key=blockSort)

        # Setup the initial address for the first transaction manually and save it
        self.addresses.addLNAddress("0.0.0.0", nodeBlocks[0]["firstNeighbourNode"])

        # Get an LN address for each node
        for nodeBlock in nodeBlocks:

            # Get the key for the node so we can reference it in the graph
            nodeKey = nodeBlock["node"]

            # Assign the LN address to the neighbour node
            neighbourAddress = self.addresses.getLNAddress(nodeBlock["firstNeighbourNode"])
            # If the neighbour doesn't have an address yet get him a random one
            if not neighbourAddress:
                neighbourAddress = self.addresses.getNewRandomLNAddress()
                self.addresses.addLNAddress(neighbourAddress, nodeKey)

            # Get an address related to our neighbour if we don't have one
            if not self.addresses.getLNAddress(nodeKey):
                # Save this address
                self.addresses.addLNAddress(self.addresses.getNewRelatedLNAddress(neighbourAddress), nodeKey)

        # Visualize graph with addresses
        nx.draw(G, with_labels=True, labels=self.addresses.getAddressesDic(), font_size=16, label="Leftover LN")
        plt.show()

        # Add routing tables
        for node in nodes:
            nodeAddress = self.addresses.getLNAddress(node)

            # Build the channels
            for neighbour, channelData in G[node].items():
                neighbourNodeAddress = self.addresses.getLNAddress(neighbour)
                self.channels[nodeAddress][neighbourNodeAddress] = channelData[neighbour]

            self.addRoutingTable(nodeAddress)

        # Simulate that nodes have exchanged n routing updates
        self.exchangeRoutingUpdates(len(nodes)**2)

        print("Distributed Routing: Initial routing setup done.")

        return

    # Add a routing table
    def addRoutingTable(self, address):

        for neighbour in self.channels[address].keys():
            self.routingTables[address][neighbour] = hop.Hop(neighbour, self.channels[address][neighbour])

        return

    # Share updates through every edge n times
    def exchangeRoutingUpdates(self, n):

        # print("Sharing " + str(n) + " routing updates")

        # Get a list of all addresses in a random order
        addresses = list(self.channels)
        random.shuffle(addresses)

        # Go through every edge n times
        for _ in range(0, n):

            # Go through every node
            for address in addresses:
                
                # Go through every channel in each node
                for neighbour in list(self.channels[address]):
                
                    # Share the entire routing table with the neighbour
                    for destination in self.routingTables[address]:

                        if destination == neighbour:
                            continue

                        # If the neighbour already knows about the destination
                        if destination in self.routingTables[neighbour]:

                            # If the hop is the neighbour we don't share
                            if self.routingTables[address][destination].hop == neighbour:
                                continue

                            new_max_money = min(self.routingTables[address][destination].max_money,
                                                self.channels[neighbour][address])

                            # If we are updating old info from this address
                            if self.routingTables[neighbour][destination].hop == address:
                                self.routingTables[neighbour][destination] = hop.Hop(address, new_max_money)

                            elif self.routingTables[neighbour][destination].max_money < new_max_money:
                                self.routingTables[neighbour][destination] = hop.Hop(address, new_max_money)

                        else:
                            max_money = min(self.channels[neighbour][address], self.routingTables[address][destination].max_money)
                            self.routingTables[neighbour][destination] = hop.Hop(address, max_money)

        return

    # Get a path from node A to node B by following the routing table information starting from A
    def getRoutingPath(self, source, destination):

        print("Distributed Routing: Getting routing path from " + source + " to " + destination)

        nextHop = source
        path = [nextHop]
        nextHopTable = self.routingTables[nextHop]
        hopCounter = 0

        while destination in nextHopTable.keys():
            
            # Limit the paths to 20 hops
            if hopCounter > 20:
                print("Distributed Routing: Hops limit reached.\n")
                break

            print("\nPATH:\nFrom: " + source + "\nTo: " +
                  destination + "\nCurrent Hop: " + nextHop)
            print("\nTABLE:\n" + str(nextHopTable) + "\n")
            nextHop = nextHopTable[destination].hop
            path.append(nextHop)
            nextHopTable = self.routingTables[nextHop]

            # If the next hop is the destination we reached the end of the path
            if destination == nextHop:
                print("Distributed Routing: Reached " + destination + "!" + "\nPath:")
                print(path)
                return path
            
            hopCounter+=1

        print("\nDistributed Routing: Couldn't find path to: " + destination + "\n")

        return None

    # Simulate the payment and change the channel states accordingly. If the path was not found return 1.
    # If the path is not valid (not enough capacity) return 2. If the payment was successful then return 0.
    def simulatePayment(self, source, destination, amount):

        sourceAddress = self.addresses.getLNAddress(source)
        destinationAddress = self.addresses.getLNAddress(destination)

        path = self.getRoutingPath(sourceAddress, destinationAddress)

        # Check if there is a path
        if not path:
            # If there isn't return -1
            return -1

        # Find if the payment can go through
        for i in range(0, len(path) - 1):

            node1 = path[i]
            node2 = path[i + 1]

            # If one of the channels has not enough capacity the path is not valid
            if self.channels[node1][node2] < amount:
                # If there isn't enough capacity on a path channel return -2
                print("Distributed Routing: Invalid path. Not enough balance on: " + node1 + " -> " + node2)
                return -2


        # Change the state of the channels in the path
        for i in range(0, len(path) - 1):
            node1 = path[i]
            node2 = path[i + 1]

            self.channels[node1][node2] -= amount
            self.channels[node2][node1] += amount

        self.exchangeRoutingUpdates(self.nRoutingGossip)

        return len(path)
