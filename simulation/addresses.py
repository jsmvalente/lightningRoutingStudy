import tree

class Addresses:

    def __init__(self):
        self.addressTree = tree.Tree()

    def suggestNewAddress(self, neighbourAddress):
            # Use the address that's closer to the neighbour address
            newAddress = self.addressTree.getSimilarAddress(neighbourAddress)

            if newAddress:
                return newAddress
            else:
                # Had an error while looking up a new address and the return was null
                return None

    def addAddress(self, address):
        self.addressTree.addAddress(address)

        return

