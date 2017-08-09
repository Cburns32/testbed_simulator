import simpy
import numpy as np

class FinishedParts(object):
    def __init__(self, env, name, end_count):
        self.env = env
        self.name = name
        self.end_count = end_count
        self.part_store = simpy.Store(env)
        self.process = env.process(self.experiment_tracker())

    def calc_pph(self,s,n):
        t0 = float(s[0].tracker_array[9])
        t1 = float(s[n-1].tracker_array[9])
        return ((n-1) / (t1 - t0)) * 3600

    def pph(self):
        return "{:.3f}".format( self.calc_pph(self.part_store.items, len(self.part_store.items)) )
        # for part in self.part_store.items:
        #     print part.log()

    def calc_tpp(self):
        pt = []
        for p in self.part_store.items:
            if not p.id == 1:   # Ignore the first part, as the testbed is purged
                pt.append(float(p.tracker_array[9]) - float(p.tracker_array[1]))
        return [ np.mean(pt), np.std(pt) ]

    def tpp(self):
        result =  self.calc_tpp()
        return "{:.3f},{:.3f}".format( result[0], result[1] )

    def amount(self):
        return str(len(self.part_store.items))

    def experiment_tracker(self):
        while True:
            if len(self.part_store.items) >= self.end_count:
                #stats.compute_stats(finished)
                self.env.exit()
            yield self.env.timeout(1.0)
