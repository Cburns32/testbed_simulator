import simpy, random

class Link(object):

    def __init__(self, env, name, node1, node2):
        self.env = env
        self.link_rx_buff = None
        self.link_tx_buff = None
        self.name = name
        self.n1 = node1
        self.n2 = node2
        self.busy = False
        self.msg_cntr = 0
        #Disturbance Variables
        self.disturbance_delay = True
        self.delay_mu = 0.005
        self.delay_sigma = 0.0
        # Processes
        self.rx_proc = self.env.process(self.link_rx_task())
        self.tx_proc = self.env.process(self.link_tx_task())

    # Helper function alias for readability
    def tx(self,msg):
        self.link_receive(msg)

    # Helper function alias for readability
    def rx(self):
        #self.link_receive(msg)
        if(self.link_tx_buff != None):
            return_value = self.link_tx_buff
            self.link_tx_buff = None
            return return_value
        else:
            return None

# RECEIVE (FROM NODE) FUNCTIONS

    def link_receive(self,msg):
        self.msg_cntr += 1
        self.link_rx_buff = msg
        self.busy = True
        self.rx_proc.interrupt()

    def link_rx_task(self):
        while True:
            try:
                yield self.env.timeout(10.0)
            except simpy.Interrupt:
                if self.link_rx_buff == "get_mbtcp":
                    self.tx_proc.interrupt()
                    self.link_rx_buff = None

# TRANSMIT (FROM NODE) FUNCTIONS

    def transmit(self):
        #self.n1.rx(self.link_tx_buff)
        self.link_tx_buff = self.n2.state
        self.busy = False

    def link_tx_task(self):
        while True:
            try:
                yield self.env.timeout(10.0)
            except simpy.Interrupt:
                if self.disturbance_delay:
                    delay = abs(random.normalvariate(self.delay_mu,self.delay_sigma))
                    #print "Delay: " + str(delay)
                    yield self.env.timeout(delay)
                self.transmit()
