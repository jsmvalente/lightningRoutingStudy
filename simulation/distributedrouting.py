import LNAddresses
import routingTables

class DistributedRouting:

    def __init__(self, G):

        self.G = G
        self.addresses = LNAddresses.LNAddresses()
        self.routingTables = routingTables.routingTables()

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
        for nodeBlock in nodeBlocks:

            nodeKey = nodeBlock["node"]
            address = self.addresses.getLNAddress(nodeKey)

            # Find the neighbours of the node so we can add added it to the routing tables
            neighbourAddresses = []
            for neighbour, channelData in G[nodeKey].items():
                neighbourAddresses.append(self.addresses.getLNAddress(neighbour))

            self.routingTables.addRoutingTable(address, neighbourAddresses)

        # Simulate that sometime has passed and nodes have exchanged routing updates
        for _ in range(3):
            self.routingTables.exchangeRoutingUpdates()

        return

    # Simulate the payment and change the channel states accordingly. If the path was not found return 1.
    # If the path is not valid (not enough capacity) return 2. If the payment was successful then return 0.
    def simulatePayment(self, source, destination, amount):

        path = self.routingTables.getRoutingPath(self.addresses.getLNAddress(source), self.addresses.getLNAddress(destination))

        # Check if there is a path
        if not path:
            # If there isn't return -1
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
