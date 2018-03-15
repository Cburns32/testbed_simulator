
# Author: Timothy Zimmerman (timothy.zimmerman@nist.gov)
# Organization: National Institute of Standards and Technology
# U.S. Department of Commerce
# License: Public Domain
#
# An attempt to emulate the network communications required between the processes.
# The code executes as expected, however there is more functionality to be desired,
# especially in regards to reproducing the effects of a TCP/IP stack. This file
# consolidates all of the classes required for network functionality.
#
# When creating a link between objects, 'sockets' are created and tracked by name.
# Each socket has the ability to hold one 'packet'. Packet objects are not actually
# transferred between objects; the objects themselves will apply the configured
# delays, gather the necessary information based on the message type, apply the
# return delay, and wait to be retrieved by the object that transmitted it.
#
# Each object that transmits packets using this class will poll the socket to
# determine when a packet is ready to be retrieved.
#
# Future work will obsolete this class.
#

import simpy, random, logger

# Packet class. This object has its own process that registers with the simpy env.
# It independently gathers the information defined by the message type while
# applying TX and RX delay. Once complete, the object triggers the callback.
class Packet(object):
    def __init__(self, env, msg, dest_node, cb):
        self.env = env # Store a local reference to the simpy environment
        self.msg = msg # String of the message type
        self.n = dest_node # Defines the object name where the data can be found
        self.reply = None
        # Callback used to signal the socket to update its state
        self.callback = cb
        # Create the Packet process in the simpy environment
        self.proc = self.env.process(self.packet_task())

    # Calculates a propagation delay based on the normal distribution
    # https://docs.python.org/2/library/random.html#random.normalvariate
    # TODO Add configuration for link characteristics
    def delay(self, prop_delay):
        d = random.normalvariate(prop_delay[0],prop_delay[1])
        # The normal distribution can produce negative numbers; we must catch these
        if d < 0: return 0.0
        return d

    # Actions the packet can perform based on the message type. IF statement
    # structure will determine the message type and execute the specific actions.
    # Actions gather data from the destination object; the packet is not
    # transmitted to the destination object.
    def actions(self):
        m = self.msg
        if m == "get_mbtcp":
            self.reply = self.n.state
        elif m == "Robot1_get_job":
            self.reply = self.n.r1_job
        elif m == "Robot2_get_job":
            self.reply = self.n.r2_job
        elif "robot_prox" in m:
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

    # Simpy process for the Packet object.
    def packet_task(self):
        # TX propagation delay
        yield self.env.timeout( self.delay([0.001, 0.0]) )
        # Perform packet actions (e.g., get/set data in destination node)
        self.actions()
        # RX propagation delay
        yield self.env.timeout( self.delay([0.001, 0.0]) )
        # Inform the socket this message has completed its journey
        self.callback()

# Socket class. Socket objects have to be created to allow multiple packets to
# be sent at a time. A link may have multiple sockets, but only one packet may
# occupy a socket until retrieved by the transmitting object. Sockets are named
# with strings. Packets will inform the socket once its journey is complete by
# calling the response_notify callback function. The packet is stored in the
# variable self.medium.
class Socket(object):
    def __init__(self, env, name, dest_node):
        self.env = env # Store a local reference to the simpy environment
        self.name = name # String name of the socket
        self.n = dest_node # Defines the object name where the data can be found
        self.medium = None # Where the packet object resides
        self.busy = False
        self.response = False # True if response 'received' from destination

    # Called by Link to create the packet and initiate the transmission
    def send_packet(self, msg):
        if not self.busy: # If we don't already have a packet underway...
            self.busy = True
            # Create the packet--everything else at this point is automatic
            # and handled by the Packet object
            self.medium = Packet(self.env, msg, self.n, self.response_notify)

    # Callback function for the Packet object, once its journey has completed
    def response_notify(self):
        self.busy = False
        self.response = True # Response was 'received'

    # Remove the packet from the medium, and return it to the Link
    def pop_packet(self):
        pkt = self.medium
        self.medium = None
        self.busy = False
        self.response = False
        return pkt

# Link object for a network-based Testbed object. Each link is between two
# specific Testbed objects. The reference to this object is held in the self.n
# variable. Each link can have multiple message types that are sent between them,
# so sockets are provided (one per message type). Disturbance variables are not
# used at this time--hardcoded delays are evident in the Packet object process.
# Transmission of a packet is triggered by a Testbed object. However, retrieval
# of a packet is done by POLLING a Link Socket with the 'socket_response' function.
# Returned packet data is retrieved with the 'get_packet' function. The returned
# data is of the same type within the destination object.
class Link(object):
    def __init__(self, env, name, dest_node, sockets):
        self.env = env
        self.name = name
        self.n = dest_node
        self.sockets = {}
        self.msg_count = 0 # NOT IMPLEMENTED
        #Disturbance Variables -- NOT IMPLEMENTED
        self.delay_mu = 0.01
        self.delay_sigma = 0.0
        # 'sockets' parameter should be a list of string names
        for sock in sockets:
            self.socket_open(sock)

    # Create a new socket
    def socket_open(self, name):
        self.sockets[name] = Socket(self.env, name, self.n)

    # Check if a socket is busy
    def socket_busy(self, name):
        return self.sockets[name].busy

    # Check if a socket has a returned packet available
    def socket_response(self, name):
        return self.sockets[name].response

    # Send a packet over the socket of type 'msg'
    def send_packet(self, socket, msg):
        self.sockets[socket].send_packet(msg)

    # Return the packet object to the requestor
    def get_packet(self, socket):
        return self.sockets[socket].pop_packet()
