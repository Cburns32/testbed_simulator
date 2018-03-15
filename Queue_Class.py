
# Author: Timothy Zimmerman (timothy.zimmerman@nist.gov)
# Organization: National Institute of Standards and Technology
# U.S. Department of Commerce
# License: Public Domain
#
# Instantiates part objects for use by testbed. Robot 1 obtains its parts from
# this object.

import simpy, logger
from Part_Class import Part

class Queue(object):
    def __init__(self, env, name):
        self.env = env # Store a local reference to the simpy environment
        self.name = name
        self.part_counter = 0 # Counter for assigned IDs to parts
        # We only need to hold one part. The class will instantiate a new part
        # and put it in the store before Robot 1 needs another one.
        self.part_store = simpy.Store(env, capacity=1)
        # Create the PLC process in the simpy environment
        self.process = self.env.process(self.queue_task())

    # Convenience function - Returns a string representation of the ID (part
    # number) of the part currently residing in the queue.
    def part_num(self,store):
        return str(self.part_store.items[0].get_id())

    # Convenience function - Returns True if there is a part available in the queue.
    def part_available(self):
        if len(self.part_store.items) > 0:
            return True
        return False

    # Simpy process for the Queue object
    def queue_task(self):
        # Process loop
        while True:
            # Instantiate a new part if the queue is empty, and put it in the store
            if len(self.part_store.items) == 0:
                self.part_counter += 1
                self.part_store.put(Part(self.part_counter, self.env.now))
                logger.debug("Created part: " + self.part_num(self.part_store),self.name,self.env.now)
            yield self.env.timeout(1.0)
