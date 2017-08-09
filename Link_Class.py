import simpy, random, logger

class Packet(object):
    def __init__(self, env, msg, dest_node, cb):
        self.env = env
        self.msg = msg
        self.n = dest_node
        self.reply = None
        self.busy = True
        # Callback used to signal the link to inspect the packet state
        self.callback = cb
        # Process
        self.proc = self.env.process(self.packet_task())

    def busy(self):
        return self.busy

    def delay(self, prop_delay):
        d = random.normalvariate(prop_delay[0],prop_delay[1])
        # The distribution can produce negative numbers, so we must catch these
        if d < 0: return 0.0
        return d

    def actions(self):
        m = self.msg
        #self.info("Running actions")
        if m == "get_mbtcp":
            self.reply = self.n.state
        elif m == "Robot1_get_job":
            self.reply = self.n.r1_job
        elif m == "Robot2_get_job":
            self.reply = self.n.r2_job
        elif "robot_prox" in m: # This value gets chosen for all PROX messages, the elif then falls out
            if "true" in m:
                val = True
            else:
                val = False
            if   "s1" in m:
                self.n.s1_prox = val
            elif "s2" in m:
                self.n.s2_prox = val
            elif "s3" in m:
                self.n.s3_prox = val
            elif "s4" in m:
                self.n.s4_prox = val
            self.reply = "OK"
        elif "set_prox" in m:
            if "true" in m:
                self.n.robot_prox = True
            else:
                self.n.robot_prox = False
            self.reply = "OK"

    def packet_task(self):
        # TX propagation delay
        yield self.env.timeout( self.delay([0.001, 0.0]) )
        # Perform packet actions (e.g., get/set data at destination node)
        self.actions()
        # RX propagation delay
        yield self.env.timeout( self.delay([0.001, 0.0]) )
        self.busy = False
        # Inform the link that this message has completed its tasks
        self.callback()


class Socket(object):
    def __init__(self, env, name, dest_node):
        self.env = env
        self.name = name
        self.n = dest_node
        self.medium = None
        self.busy = False
        self.response = False

    def send_packet(self, msg):
        if not self.busy:
            self.busy = True
            self.medium = Packet(self.env, msg, self.n, self.response_notify)

    def response_notify(self):
        self.busy = False
        self.response = True

    def pop_packet(self):
        pkt = self.medium
        self.medium = None
        self.busy = False
        self.response = False
        return pkt


class Link(object):
    def __init__(self, env, name, dest_node, sockets):
        self.env = env
        self.name = name
        self.n = dest_node
        self.sockets = {}
        self.msg_count = 0
        #Disturbance Variables
        self.delay_mu = 0.01
        self.delay_sigma = 0.0
        # 'sockets' parameter should be a list of string names
        for sock in sockets:
            self.socket_open(sock)

    def socket_open(self, name):
        self.sockets[name] = Socket(self.env, name, self.n)

    def socket_busy(self, name):
        return self.sockets[name].busy

    def socket_response(self, name):
        return self.sockets[name].response

    def send_packet(self, socket, msg):
        self.sockets[socket].send_packet(msg)

    def get_packet(self, socket):
        return self.sockets[socket].pop_packet()
