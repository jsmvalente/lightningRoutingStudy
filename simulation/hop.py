class Hop:

    def __init__(self, hop, max_money):

        self.hop = hop
        self.max_money = max_money
        return

    def __repr__(self):
        return "(Address:" + str(self.hop) + " Max. Vol.:, " + str(self.max_money) + ")"
