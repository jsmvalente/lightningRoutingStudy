import ipaddress
from bitstring import BitArray

class Tree:

    # Define a Node Class
    class Node:
        def __init__(self):
            self.right = None
            self.left = None
            self.parent = None

    def __init__(self):
        # The root corresponds to the LSB
        self.root = self.Node()

        return

    # Check if the address list is empty
    def isEmpty(self):
        if not self.root.right and not self.root.left:
            return True

        return False

    def addAddress(self, address):

        # Get the address in bit form, lest least significant bit first
        byteAddress = ipaddress.IPv4Address(address).packed
        bitAddress = BitArray(bytes=byteAddress).bin[::-1]

        helperPointer = self.root
        for bit in bitAddress:

            # If the bit is logical 1
            if bit:
                # If the helper pointer is not null, meaning this path was crossed before
                if helperPointer.right:
                    # Continue going down the tree
                    helperPointer = helperPointer.right
                # If it was not we create a new node and make the helper pointer point to it
                else:
                    # Build the tree further down
                    newNode = self.Node()
                    newNode.parent = helperPointer
                    helperPointer.right = newNode
                    helperPointer = helperPointer.right

            # If the bit is logical 0
            else:
                # If the helper pointer path is not null, meaning this path was crossed before
                if helperPointer.left:
                    # Continue going down the tree
                    helperPointer = helperPointer.left
                # If it was not we create a new node and make the helper pointer point to it
                else:
                    # Build the tree further down
                    newNode = self.Node()
                    newNode.parent = helperPointer
                    helperPointer.left = newNode
                    helperPointer = helperPointer.left

        return

    def getAddressFromNeighbour(self, neighbourAddress):

        # Get the address in bit form, LSB first
        byteAddress = ipaddress.IPv4Address(neighbourAddress).packed
        bitAddress = BitArray(bytes=byteAddress).bin[::-1]

        # Navigate to the neighbour address in the tree
        helperPointer = self.root
        for bit in bitAddress:

            # If the bit is logical 1
            if bit:
                helperPointer = helperPointer.right

            # If the bit is logical 0
            else:
                helperPointer = helperPointer.left

        # Navigate up the tree and reverse the address to map the path backwards
        bitAddressMSB = bitAddress[::-1]
        exploreRoot = helperPointer
        for index, bit in enumerate(bitAddressMSB):

            # Go up in the tree by one node
            exploreRoot = exploreRoot.parent

            # Check if other side (searchHead) is null
            if bit:
                searchHead = exploreRoot.parent.left

                if not searchHead:
                    address = ("0" + bitAddressMSB[index+1:]).zfill(32)
                    ipv4Address = ipaddress.IPv4Address()
                    return str(ipv4Address)
            else:
                searchHead = exploreRoot.parent.right

                if not searchHead:
                    address = ("1" + bitAddressMSB[index+1:]).zfill(32)
                    ipv4Address = ipaddress.IPv4Address()
                    return str(ipv4Address)

            # If the search head is not null we try to find new addresses using a DFS



        return
