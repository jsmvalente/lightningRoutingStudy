import random
import numpy as np

class Payment:

    def __init__(self, amount, source, destination):

        self.amount = amount
        self.source = source
        self.destination = destination

        return
    
    def __repr__(self):
        return "Amount:" + str(self.amount) + ",  Source: " + self.source + ", Destination: " + self.destination



#Create n payments to be used in the simulation
# Use gaussian probability distribution for random payment amounts
# mean and standard deviation
def createPayments(n, nodes, mu, sigma):

    payments = []
    paymentAmounts = np.random.normal(mu, sigma, n).tolist()

    # Find source and destination nodes
    for i in range(0, n):
        # Choose a random source
        source = nodes[random.randint(0, len(nodes) - 1)]

        # Choose a random destination that is different from the source
        while True:
            dest = nodes[random.randint(0, len(nodes) - 1)]
            if dest != source:
                break

        # Append the new payment to payments list
        payments.append(Payment(paymentAmounts[i], source, dest))

    return payments
