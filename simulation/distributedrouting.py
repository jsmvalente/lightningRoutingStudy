import LNAddresses
import random
from collections import defaultdict

class DistributedRouting:

    def __init__(self, G):

        self.G = G
        # Routing Tables:
        #   → Node Address
        #       → Destination
        #           → Next Hop
        #               Capacity: 1000
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

            # Assign the LN address to the node
            neighbourAddress = self.addresses.getLNAddress(nodeBlock["firstNeighbourNode"])
            # If the neighbour doesn't have an address yet get him a random one
            if not neighbourAddress:
                neighbourAddress = self.addresses.getNewRandomLNAddress()
                self.addresses.addLNAddress(neighbourAddress, nodeKey)

            # Get an address related to our neighbour if we don't have one
            if not self.addresses.getLNAddress(nodeKey):
                # Save this address
                self.addresses.addLNAddress(self.addresses.getNewRelatedLNAddress(neighbourAddress), nodeKey)

        # Add routing tables in order of appearance
        for node in nodes:
            nodeAddress = self.addresses.getLNAddress(node)

            # Build the channels info dictionary
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

            self.routingTables[address][neighbour] = {neighbour: self.channels[address][neighbour]}
            # Add nieghbour to node update queue, meaning we have new info on how to get to the neighbour
            self.updateQueues[address].append(neighbour)

        return

    # In a random node order, share the routing table of a node with its neighbours and update the
    # neighbours routing tables accordingly
    def exchangeRoutingUpdates(self):

        print("Sharing routing updates")

        # Get a random node order to update the tables
        addresses = list(self.routingTables.keys())
        random.shuffle(addresses)

        for address in addresses:

            # Get the updates that are ready to be sent to the neighbours
            updateQueue = self.updateQueues[address]

            print("Sharing " + address + " updates.")

            # Loop through updates and apply them to the neighbours
            print("updateQueue size: " + str(len(updateQueue)) + " updates")
            while len(updateQueue) > 0:
                update = updateQueue.pop(0)
                destination = update["destination"]
                maxCapacity = update["maxCapacity"]

                # Share the table with the neighbours and update their table accordingly
                for neighbour in self.channels[address].keys():

                    # Check if we are not sharing info with the neighbour about itself
                    if destination != neighbour:

                        neighbourTable = self.routingTables[neighbour]
                        neighbourUpdateQueue = self.updateQueues[neighbour]

                        # Find if we are a bottleneck to the path, if we are update the max capacity
                        if self.channels[neighbour][address] < maxCapacity:
                            maxCapacity = self.channels[neighbour][address]

                        # Get the neighbours next hop for a certain the update's destination
                        try:
                            hops = neighbourTable[destination]
                        except KeyError:
                            neighbourTable[destination] = {}
                            hops = neighbourTable[destination]

                        # If next hop address is already listed we change it according to the new info
                        # If we have less than three addresses we also add the new next hop
                        if address in hops.keys() or len(hops) < 3:
                            hops[address] = maxCapacity
                            neighbourUpdateQueue.append({"destination": destination, "maxCapacity": maxCapacity})
                        # If the list already has 3 addresses only add the new next hop if its capacity its bigger
                        else:
                            minCapacity = 99999999999
                            minCapacityAddress = None
                            for hopAddress, capacity in hops.items():
                                if capacity < minCapacity:
                                    minCapacity = capacity
                                    minCapacityAddress = hopAddress

                            if minCapacity < maxCapacity:
                                del hops[minCapacityAddress]
                                hops[address] = maxCapacity
                                neighbourUpdateQueue.append({"destination": address, "maxCapacity": maxCapacity})

        return

    # Get a path from node A to node B by following the routing table information starting from A
    def getRoutingPath(self, source, destination):

        print("Getting routing path from " + source + " to " + destination)

        nextHop = source
        path = [nextHop]
        nextHopTable = self.routingTables[nextHop]

        while destination in nextHopTable.keys():
            nextHops = nextHopTable[destination]

            maxCapacity = 0
            print(nextHops)
            for address, capacity in nextHops.items():
                if capacity > maxCapacity:
                    maxCapacity = capacity
                    nextHop = address

            path.append(nextHop)
            nextHopTable = self.routingTables[nextHop]

            # If the next hope is the destination we reached the end of the path
            if destination == nextHop:
                return path

        return None

    # Simulate the payment and change the channel states accordingly. If the path was not found return 1.
    # If the path is not valid (not enough capacity) return 2. If the payment was successful then return 0.
    def simulatePayment(self, source, destination, amount):

        sourceAddress = self.addresses.getLNAddress(source)
        destinationAddress = self.addresses.getLNAddress(destination)

        path = self.getRoutingPath(sourceAddress, destinationAddress)

        # Check if there is a path
        if not path:
            # If there isn't return -1/USD 262.65
            return -1

        # Get the LN addresses in the path in key for
        for i in range(0, len(path)):
            path[i] = self.addresses.getAddress(path[i])

        # Find if the payment can go through
        for i in range(0, len(path) - 2):

            node1 = path[i]
            node2 = path[i + 1]

            # If one of the channels has not enough capacity the path is not valid
            if self.G[node1][node2][node1] < amount:
                # If there isn't enough capacity on a path channel return -2
                return -2


        # Change the state of the channels in the path
        for i in range(0, len(path) - 2):
            node1 = path[i]
            node2 = path[i + 1]

            self.G[node1][node2][node1] -= amount
            self.G[node1][node2][node2] += amount

            #self.routingTables.exchangeRoutingUpdates()

        return len(path)
