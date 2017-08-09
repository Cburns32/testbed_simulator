import simpy, random

class Packet(object):

    def __init__(self, env, idv, msg, dest_node, cb):
        self.env = env
        self.idv = idv # Unique ID
        self.msg = msg
        self.dest_node = dest_node
        self.reply = None
        self.busy = True
        # Callback used to signal the link to inspect the packet state
        self.callback = cb
        # Process
        self.proc = self.env.process(self.packet_task())

    def busy(self):
        return self.busy

    def delay(self, prop_delay):
        d = abs(random.normalvariate(prop_delay[0],prop_delay[1]))
        return d

    def tasks(self):
        m = self.msg
        if m == "get_mbtcp":
            self.msg_out = self.dest_node.state
        elif m == "Robot1_get_job":
            self.msg_out = self.dest_node.r1_job
        elif m == "Robot2_get_job":
            self.msg_out = self.dest_node.r2_job
        elif "prox" in m:
            if "true" in m: val = True
            else: val = False
            if   "s1" in m:
                self.dest_node.s1_prox = val
            elif "s2" in m:
                self.dest_node.s2_prox = val
            elif "s3" in m:
                self.dest_node.s3_prox = val
            elif "s4" in m:
                self.dest_node.s4_prox = val
            self.reply = "OK"
        elif "set_prox" in m:
            if "true" in m:
                self.dest_node.robot_prox = True
            else:
                self.dest_node.robot_prox = False
            self.reply = "OK"

    def packet_task(self):
        #while True:
        # TX propagation delay
        yield self.env.timeout( self.delay([0.01, 0.0]) )
        # Perform tasks (e.g., get/set data at destination node)
        self.tasks()
        # RX propagation delay
        # self.delay(rx_delay)
        self.busy = False
        # Inform the link that this message has completed its tasks
        self.callback(self)
