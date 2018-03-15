
# Author: Timothy Zimmerman (timothy.zimmerman@nist.gov)
# Organization: National Institute of Standards and Technology
# U.S. Department of Commerce
# License: Public Domain
#
# Stores all of the Part objects created by the simulated testbed. This class is
# used to:
#   a) keep track of the number of parts produced;
#   b) keep all part data for logging, metrics, and KPI calculations; and
#   c) trigger the experiment to terminate once the configured amount of parts
#      have been manufactured

import simpy
import numpy as np

class FinishedParts(object):

    def __init__(self, env, name, end_count):
        self.env = env # Store a local reference to the simpy environment
        self.name = name
        self.end_count = end_count
        self.part_store = simpy.Store(env) # Create a store for finished parts
        # Create the FinishedParts process in the simpy environment
        self.process = env.process(self.experiment_tracker())

    # Calculates the parts-per-hour KPI
    def calc_pph(self,s,n):
        t0 = float(s[0].tracker_array[9])
        t1 = float(s[n-1].tracker_array[9])
        return ((n-1) / (t1 - t0)) * 3600

    # Returns the parts-per-hour KPI in a string format
    def pph(self):
        return "{:.3f}".format( self.calc_pph(self.part_store.items, len(self.part_store.items)) )

    # Calculates the time-per-part KPI
    def calc_tpp(self):
        pt = []
        for p in self.part_store.items:
            if not p.id == 1:   # Ignore the first part, as the testbed is purged
                pt.append(float(p.tracker_array[9]) - float(p.tracker_array[1]))
        return [ np.mean(pt), np.std(pt) ]

    # Returns the time-per-part KPI in a string format
    def tpp(self):
        mean,stddev =  self.calc_tpp()
        return "{:.3f},{:.3f}".format( mean, stddev )

    # Returns the amount of finished parts in the store as a string
    def amount(self):
        return str(len(self.part_store.items))

    # Simpy process for the FinishedParts object. This process will continue
    # executing every 1.0 second (sim time) until the amount of parts specified
    # in self.end_count is reached. The env monitors this process. Once the process
    # dies, the env kills the simulation.
    def experiment_tracker(self):
        while True:
            if len(self.part_store.items) >= self.end_count:
                #stats.compute_stats(finished)
                self.env.exit()
            yield self.env.timeout(1.0)
