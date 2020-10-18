import tree
from random import getrandbits
from ipaddress import IPv4Address

class LNAddresses:

    def __init__(self):
        self.addressTree = tree.Tree()
        self.addressesDic = {}
        self.lnAddressesDic = {}

    def getNewRandomLNAddress(self):

        # Get random addresses until we find one that doesn't is not used yet
        while True:
            bits = getrandbits(32)  # generates an integer with 32 random bits
            address = IPv4Address(bits)  # instances an IPv4Address object from those bits
            randomAddress = str(address)  # get the IPv4Address object's string representation

            if not self.addressTree.addressExists(randomAddress):
                return randomAddress

    def getAddressesDic(self):
        return self.lnAddressesDic

    def getNewRelatedLNAddress(self, neighbourAddress):
        # Use the address that's closer to the neighbour address
        newAddress = self.addressTree.getRelatedAddress(neighbourAddress)

        if newAddress:
            return newAddress
        else:
            # Had an error while looking up a new address and the return was null
            return None

    def addLNAddress(self, address, node):
        self.addressTree.addAddress(address)
        self.lnAddressesDic[node] = address
        self.addressesDic[address] = node
        # print("Address '" + address + "' added to the database.")

        return


    def getLNAddress(self, node):
        try:
            address = self.lnAddressesDic[node]
            return address
        except:
            return None

    def getAddress(self, lnAddress):
        return self.addressesDic[lnAddress]
