import simpy
import random
import logger


# TODO Implement logger
# TODO Return connection status

class Switch(object):
    def __init__(self, env, name, msg, mac, ip, port):
        self.env = env # Store a local reference to the simpy environment
        self.msg = msg # String of the message type
        self.mac = mac # Define general mac address variable
        self.ip = ip   # Define general ip address variable
        self.port = port_assigned # Defines port for device to sit on (each port is an element in portList)
        self.avail_ports = True # Used to avoid cache of more devices than ports available
        self.total_ports = 8    # 8 ports on switch
        # self.ports_disconnected = []
        self.cache = {} # Definition of all device information (definitiions contained in PortList)
        self.portList = [] # Dontains each connected devices' information
        self.fifo_tracker = 0 # This keeps track of the order each device is
                              # stored in cache (should be same sequential order as portList appears)

# store_cache function is used to record device name, mac, ip, port in a list of device definitions
    def store_cache(msg, name, mac, ip, port_assigned):
        if self.msg == 'Sending' and self.avail_ports == True:
            self.fifo_tracer += 1
            self.cache = {'name':self.name, 'mac':self.mac, 'ip':self.ip, 'Queue':self.fifo_tracker, 'port_assigned':self.port_assigned}
            self.portList.append(cache)
            self.msg = 'Stored'
        if self.msg == 'Sending' and self.avail_ports == False:
            self.msg = 'Error: All ports taken'

# port_disconnected function is used to remove device from cache table
# While msg == disconnect port, this searches for specific element with correct port_assigned,
# then deletes it from portList
    def port_disconnected(self, msg, port_assigned):
        if self.msg == 'Disconnected port: ' + str(port_assigned):
            port_dc = port_assigned
            for port_assigned in cache.keys():
                if port_assigned == port_dc:
                    del portList[fifo_tracer -1]
            self.msg = 'Removed from cache'

# port_capacity prevents prevents too many entries from entering cache
    def port_capacity(self, msg, ports_occupied, avail_ports):
        if self.msg == 'Stored':
            self.ports_occupied += 1
        if self.msg =='Removed':
            self.ports_occupied -= 1
        while self.ports_occupied < self.total_ports:
            self.avail_ports = True
        while self.ports_occupied >= self.total_ports:
            self.avail_ports = False
