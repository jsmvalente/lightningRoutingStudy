import random
from collections import defaultdict

class routingTables:
    def __init__(self):
        self.routingTables = {}
        self.updateQueues = defaultdict(list)
        self.neighbours = {}
        return

    # Add a routing table
    def addRoutingTable(self, address, neighbours):

        # Decalre a dic to serve as routing table for this node
        self.routingTables[address] = {}

        # Save the neighours of this node
        self.neighbours[address] = neighbours

        for neighbour in neighbours:
            self.routingTables[address][neighbour] = neighbour
            self.updateQueues[address].append(neighbour)

        return

    # In a random node order, share the routing table of a node with its neighbours and update the
    # neighbours routing tables accordingly
    def exchangeRoutingUpdates(self):

        print("Sharing routing updates")

        # Get a random order to update the tables
        addresses = list(self.routingTables.keys())
        random.shuffle(addresses)
        loopCounter = 0

        for address in addresses:
            # Get the updates that are ready to be sent to the neighbours
            updateQueue = self.updateQueues[address]
            # Get the neighbours
            neighbours = self.neighbours[address]

            # Loop through updates and apply them to the neighbours
            while len(updateQueue) > 0:
                update = updateQueue.pop(0)

                # Share the table with the neighbours and update their table accordingly
                for neighbour in neighbours:
                    neighbourTable = self.routingTables[neighbour]
                    neighbourUpdateQueue = self.updateQueues[neighbour]

                    # Check if the neighbour already has this info and if the info is not about the neighbour,
                    # if not, add it to the neighbours updateQueue
                    try:
                        nextNode = neighbourTable[update]
                    except KeyError:
                        if update != address:
                            neighbourTable[update] = address
                            neighbourUpdateQueue.append(update)

            loopCounter += 1
            print("Updated " + str(loopCounter) + " nodes.")

        return

    # Get a path from node A to node B by following the routing table information starting from A
    def getRoutingPath(self, source, destination):

        nextHop = source
        path = [nextHop]
        nextHopTable = self.routingTables[nextHop]

        while destination in nextHopTable.keys():
            nextHop = nextHopTable[destination]
            path.append(nextHop)
            nextHopTable = self.routingTables[nextHop]

            # If the next hope is the destination we reached the end of the path
            if destination == nextHop:
                return path

        return None
