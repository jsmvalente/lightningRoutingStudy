import ipaddress
from bitstring import BitArray

class Tree:

    # Define a Node Class
    class Node:
        def __init__(self):
            self.right = None
            self.left = None
            self.parent = None
            self.address = None

    def __init__(self):
        # The root corresponds to the LSB
        self.root = self.Node()

        return

    # Check if the address list is empty
    def isEmpty(self):
        if not self.root.right and not self.root.left:
            return True

        return False

    # Returns true if the address is present in the tree, false if it isn't
    def addressExists(self, address):

        # Get the address in bit form, lest least significant bit first
        byteAddress = ipaddress.IPv4Address(address).packed
        bitAddress = BitArray(bytes=byteAddress).bin[::-1]

        helperPointer = self.root
        for bit in bitAddress:

            # If the bit is logical 1
            if int(bit):
                if helperPointer.right:
                    # Continue going down the tree
                    helperPointer = helperPointer.right
                else:
                    return False

            # If the bit is logical 0
            else:
                if helperPointer.left:
                    # Continue going down the tree
                    helperPointer = helperPointer.left
                else:
                    return False

        return True


    def addAddress(self, address):

        # Get the address in bit form, lest least significant bit first
        byteAddress = ipaddress.IPv4Address(address).packed
        bitAddress = BitArray(bytes=byteAddress).bin[::-1]

        helperPointer = self.root
        for index, bit in enumerate(bitAddress):

            # If the bit is logical 1
            if int(bit):
                # If the helper pointer is not null, meaning this path was crossed before
                if helperPointer.right:
                    # Continue going down the tree
                    helperPointer = helperPointer.right
                # If it was not we create a new node and make the helper pointer point to it
                else:
                    # Build the tree further down
                    newNode = self.Node()
                    newNode.address = (bitAddress[:index+1])[::-1]
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
                    newNode.address = (bitAddress[:index+1])[::-1]
                    newNode.parent = helperPointer
                    helperPointer.left = newNode
                    helperPointer = helperPointer.left

        return

    def getRelatedAddress(self, neighbourAddress):

        # Get the address in bit form, LSB first
        byteAddress = ipaddress.IPv4Address(neighbourAddress).packed
        bitAddress = BitArray(bytes=byteAddress).bin[::-1]

        # Navigate to the neighbour address in the tree
        helperPointer = self.root
        for bit in bitAddress:

            # If the bit is logical 1
            if int(bit):
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
            if int(bit):
                searchHead = exploreRoot.left

                if not searchHead:
                    address = ("0" + exploreRoot.address).zfill(32)
                    ipv4Address = ipaddress.IPv4Address(BitArray(bin=address).bytes)
                    return str(ipv4Address)
            else:
                searchHead = exploreRoot.right

                if not searchHead:
                    address = ("1" + exploreRoot.address).zfill(32)
                    ipv4Address = ipaddress.IPv4Address(BitArray(bin=address).bytes)
                    return str(ipv4Address)

            # If the search head is not null we try to find new addresses using a DFS
            def dfs(node):

                address = node.address

                # Don't do DFS for leaves and their parents
                if len(address) == 32:
                    return

                # Check if the node we are visiting has children on either side.
                # If it doesnt we found a new address.
                if not node.left:
                    return ("0" + address).zfill(32)
                elif not node.right:
                    return ("1" + address).zfill(32)

                leftChildResult = dfs(node.left)

                if leftChildResult:
                    return leftChildResult

                rightChildResult = dfs(node.right)

                if rightChildResult:
                    return rightChildResult


            # DFS to try and find free addresses
            dfsResult = dfs(searchHead)

            # If we found an address through the DFS we return it
            if dfsResult:
                ipv4Address = ipaddress.IPv4Address(BitArray(bin=dfsResult).bytes)
                return str(ipv4Address)

        return
