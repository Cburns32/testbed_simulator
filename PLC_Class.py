
class PLC(object):
    def __init__(self, env):
        self.env = env
        self.links = []
        self.process = self.env.process(self.plc_task())

    def add_link(self, link):
        self.links.append(link)

    def tx(self, link, msg):
        self.links[link].tx(msg)

    def plc_task(self):
        while True:
            for link in self.links:
                # Pop message from link buffer
                reply = link.rx()
                if (not reply == None) and (link.busy == False):
                    print str(self.env.now) + " " + link.name + ": " + reply
                if link.busy == False:
                    link.tx("get_mbtcp")

            # DO PLC ROBOT LOGIC

            yield self.env.timeout(0.01)
