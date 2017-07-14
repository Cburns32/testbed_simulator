import simpy

class Station(object):
    def __init__(self, env, name, mu, sigma):
        self.env = env
        self.name = name
        self.part_store = simpy.Store(env, capacity=1)
        self.state = "unloaded"
        self.mu = mu
        self.sigma = sigma
        self.process = self.env.process(self.station_task())

    def part_exists(self, store):
        return len(store.items)

    def yield_timeout(self):
        return random.normalvariate(self.mu,self.sigma)

    def station_task(self):
        while True:
            if self.part_exists(self.part_store):
                p(self.name + ": Got a part")
                self.state = "processing"
                yield self.env.timeout(self.yield_timeout())
                self.state = "finished"
                p(self.name + ": Finished")
                while part_exists(self.store):
                    yield self.env.timeout(0.10)
                self.state = "unloaded"
            yield self.env.timeout(0.10)
