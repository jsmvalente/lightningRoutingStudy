class Hop:

    def __init__(self, hop, max_money, previous=None):

        self.hop = hop
        self.max_money = max_money
        self.previous = previous
        if self.previous:
            self.list = [(self.previous.hop, self.previous.max_money)] + self.previous.list
        else:
            self.list = []

        return

    def __repr__(self):
        if not self.previous:
            return "(address:" + str(self.hop) + " cap:, " + str(self.max_money) + ")"
        else:
            return "(address:" + str(self.hop) + " cap:, " + str(self.max_money) + ")" + ", old: " + str(self.list)
