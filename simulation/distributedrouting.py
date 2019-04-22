import addresses

class DistributedRouting:

    def __init__(self, G):

        self.G = G
        self.addresses = addresses.Addresses()

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
                    firstNeighbour =  neighbour

            nodeBlocks += [{"node": node, "firstNeighbourNode": firstNeighbour, "firstBlock": firstBlock}]

            # Set the node address to None
            G.nodes[node]["address"] = None

        # Sort the nodes by their funding transaction order in the blockchain
        def blockSort(data):
            return data["firstBlock"]

        nodeBlocks.sort(key=blockSort)

        # Setup the initial address for the first transaction manually and save it
        G.nodes[nodeBlocks[0]["firstNeighbourNode"]]["address"] = "0.0.0.0"
        self.addresses.addAddress("0.0.0.0")

        # Get an LN address for each node
        for nodeBlock in nodeBlocks:

            # Get the key for the node so we can reference it in the graph
            node = nodeBlock["node"]

            # Assign the LN address to the node
            neighbourAddress = G.nodes[nodeBlock["firstNeighbourNode"]]["address"]
            # If the neighbour doesn't have an address yet get him a random one
            if not neighbourAddress:
                neighbourAddress = self.addresses.getNewRandomAddress()
                self.addresses.addAddress(neighbourAddress)

            # Get an address related to our neighbour if we don't have one
            if not G.nodes[node]["address"]:
                G.nodes[node]["address"] = self.addresses.getNewRelatedAddress(neighbourAddress)
                # Save this address
                self.addresses.addAddress(G.nodes[node]["address"])

            # Update the routing tables after each address assignment
            self.__updateRoutingTables()

        return

    # Verifies if a payment from the source to the destination with the specified amount would be successful
    def simulatePayment(self, source, destination, amount):
        return False

    # Does a round of routing table updates in a random node order
    def __updateRoutingTables(self):
        return
