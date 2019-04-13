import addresses

class DistributedRouting:

    def __init__(self, G):

        self.G = G
        self.addresses = addresses.Addresses()

        # Start by giving each node an LN address
        nodes = list(G.nodes)
        nodeBlocks = []

        # Sort nodes chronologically (timestamp of first seen on blockchain)
        for node in nodes:

            firstBlock = 999999999
            for neighbour, channelData in G[node].items():

                fundingBlock = channelData["funding_block"]

                if fundingBlock < firstBlock:
                    firstBlock = fundingBlock

            nodeBlocks += [{"node": node, "firstNeighbourNode": neighbour, "firstBlock": firstBlock}]

        # Sort the nodes by their funding transaction order in the blockchain
        def blockSort(data):
            return data["firstBlock"]

        nodeBlocks.sort(key=blockSort)

        # Setup the initial address and save it
        G.nodes[nodeBlocks[0]["firstNeighbourNode"]]["address"] = "0.0.0.0"

        self.addresses.addAddress("0.0.0.0")

        # Get an LN address for each node
        for nodeBlock in nodeBlocks:

            # Get the key for the node so we can reference it in the graph
            node = nodeBlock["node"]

            # Assign the LN address to the node
            G.nodes[node]["address"] = self.addresses.suggestNewAddress(G.nodes[nodeBlock["firstNeighbourNode"]]["address"])
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
