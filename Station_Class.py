
# Author: Timothy Zimmerman (timothy.zimmerman@nist.gov)
# Organization: National Institute of Standards and Technology
# U.S. Department of Commerce
# License: Public Domain
#
# Models the behavior of the testbed machining stations. The code used on the
# testbed stations has a true state machine implemented; this code, however, is
# written in a linear fashion, since the order-of-operations is known and constant.
# State transitions are:
#          UNLOADED -> LOADED -> PROCESSING -> FINISHED -> UNLOADED

import simpy, random, logger

class Station(object):
    def __init__(self, env, name, process_time, startup_delay):
        self.env = env # Store a local reference to the simpy environment
        self.name = name
        self.part_store = simpy.Store(env, capacity=1) # Station can hold ONE part
        self.state = "unloaded" # Initial state of the state machine
        self.process_time = process_time # Amount of time manufacturing process should take
        # Amount of time to delay the station startup. Station task execution is
        # not synchronized between stations on the testbed, so we should
        # duplicate that behavior here.
        # TODO Automate this behavior here -- not in the parent class
        self.startup_delay = startup_delay
        self.robot_prox = False
        # Create the Station process in the simpy environment
        self.process = self.env.process(self.station_task())

    # Returns number of parts in station
    def part_exists(self):
        return len(self.part_store.items)

    # Convenience function for varying the process time based on the normal distribution
    def yield_timeout(self, t):
        return random.normalvariate(t[0],t[1])

    # Convenience function for changing the station state and producing a debug message
    def change_state(self, state):
        self.state = state
        logger.debug("State: " + state,self.name,self.env.now)

    # Simpy process for the Station object
    def station_task(self):
        yield self.env.timeout(self.startup_delay) # Startup delay
        logger.info("Starting...",self.name,self.env.now)
        while True:
            if self.part_exists(): # Has a robot given us a part?
                self.change_state("loaded")
                while self.robot_prox == True: # Wait for the robot to exit the machine
                    yield self.env.timeout(0.10) # Check every 10 milliseconds
                self.change_state("processing") # Start machining the part
                yield self.env.timeout(self.yield_timeout(self.process_time))
                self.change_state("finished")
                while self.part_exists(): # Wait for the part to be removed from the machine
                    yield self.env.timeout(0.10) # Check every 10 milliseconds
                self.change_state("unloaded")
            # We don't have a part, so check again in 10 milliseconds
            yield self.env.timeout(0.10)
