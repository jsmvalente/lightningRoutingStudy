import tree

class Addresses:

    def __init__(self):
        self.addressTree = tree.Tree()

    def newAddress(self, neighbourAddress):

        # Address book is empty and we need to add the first address
        if self.addressTree.isEmpty():
            firstAddress = '0.0.0.0'

            self.addressTree.addAddress(firstAddress)

            return firstAddress

        # Use the address that's closer to the neighbour address
        return self.addressTree.getAddressFromNeighbour(neighbourAddress)
