import LNAddresses
import random
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class DistributedRouting:

    def __init__(self, G):

        self.G = G
        # Routing Tables:
        #   → Node Address:
        #       → Destination:
        #           (nextHop, maxCapacity)
        #
        self.routingTables = defaultdict(dict)
        self.addresses = LNAddresses.LNAddresses()
        self.updateQueues = defaultdict(list)
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

            # Visualize graph
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

        # Simulate that sometime has passed and nodes have exchanged routing updates
        for _ in range(3):
            self.exchangeRoutingUpdates()

        print("Initial routing setup done.")

        return

    # Add a routing table
    def addRoutingTable(self, address):

        for neighbour in self.channels[address].keys():

            self.routingTables[address][neighbour] = (neighbour, self.channels[address][neighbour])
            # Add neighbour to node update queue, meaning we have new info on how to get to the neighbour
            self.updateQueues[address].append(neighbour)

        return

    # In a random node order, share the routing table of a node with its neighbours and update the
    # neighbours routing tables accordingly
    def exchangeRoutingUpdates(self):

        print("Sharing routing updates")

        # Get a random node order to update the tables. Use 1/5 of the nodes
        addresses = list(self.routingTables.keys())
        random.shuffle(addresses)
        addresses = addresses[:int(len(addresses)/3)]

        for address in addresses:

            # Get the updates that are ready to be sent to the neighbours
            updateQueue = self.updateQueues[address]
            routingTable = self.routingTables[address]

            print("Sharing " + address + " updates.")

            # Loop through updates and apply them to the neighbours
            print("updateQueue size: " + str(len(updateQueue)) + " updates")
            while len(updateQueue) > 0:
                destination = updateQueue.pop(0)
                nextHop = routingTable[destination]

                # Share the table with the neighbours and update their table accordingly
                for neighbour in self.channels[address].keys():

                    # Check if we are not sharing info with the neighbour about itself
                    if destination != neighbour:

                        neighbourTable = self.routingTables[neighbour]
                        neighbourUpdateQueue = self.updateQueues[neighbour]

                        if destination not in neighbourTable:
                            if nextHop[1] < self.channels[neighbour][address]:
                                neighbourTable[destination] = (address, nextHop[1])
                            else:
                                neighbourTable[destination] = (address, self.channels[neighbour][address])

                            neighbourUpdateQueue.append(destination)
                        else:
                            # Get the neighbours next hop for a certain the update's destination
                            neighbourNextHop = neighbourTable[destination]

                            # If we are updating the information on the same routing
                            if neighbourNextHop[0] == address:
                                if nextHop[1] < self.channels[neighbour][address]:
                                    neighbourTable[destination] = (address, nextHop[1])
                                else:
                                    neighbourTable[destination] = (address, self.channels[neighbour][address])
                            else:
                                # If the new path is wider than the channel and the previous info
                                if nextHop[1] > neighbourNextHop[1]:
                                    if nextHop[1] < self.channels[neighbour][address]:
                                        neighbourTable[destination] = (nextHop[0], nextHop[1])
                                    else:
                                        neighbourTable[destination] = (nextHop[0], self.channels[neighbour][address])

                            if destination not in neighbourUpdateQueue:
                                neighbourUpdateQueue.append(destination)
        return

    # Get a path from node A to node B by following the routing table information starting from A
    def getRoutingPath(self, source, destination):

        print("Getting routing path from " + source + " to " + destination)

        nextHop = source
        path = [nextHop]
        nextHopTable = self.routingTables[nextHop]

        while destination in nextHopTable.keys():
            nextHop = nextHopTable[destination][0]
            path.append(nextHop)
            nextHopTable = self.routingTables[nextHop]

            # If the next hope is the destination we reached the end of the path
            if destination == nextHop:
                return path

        return None

    # Simulate the payment and change the channel states accordingly. If the path was not found return 1.
    # If the path is not valid (not enough capacity) return 2. If the payment was successful then return 0.
    def simulatePayment(self, source, destination, amount):

        self.exchangeRoutingUpdates()

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
                return -2


        # Change the state of the channels in the path
        for i in range(0, len(path) - 1):
            node1 = path[i]
            node2 = path[i + 1]

            self.channels[node1][node2] -= amount
            self.channels[node2][node1] += amount

        return len(path)
