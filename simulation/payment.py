import random
import numpy as np

class Payment:


    def __init__(self, amount, source, destination):

        self.amount = amount
        self.source = source
        self.destination = destination

        return



#Create n payments to be used in the simulation
def createPayments(n, nodes):

    payments = []

    # Use gaussian probability distribution for random payment amounts
    # mean and standard deviation
    mu, sigma = 25000, 6000
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
