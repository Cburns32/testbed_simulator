import simpy, random, logger

class Station(object):
    def __init__(self, env, name, process_time, startup_delay):
        self.env = env
        self.name = name
        self.part_store = simpy.Store(env, capacity=1)
        self.state = "unloaded"
        self.process_time = process_time
        self.startup_delay = startup_delay
        self.robot_prox = False
        self.process = self.env.process(self.station_task())

    def part_exists(self):
        return len(self.part_store.items)

    def yield_timeout(self, t):
        return random.normalvariate(t[0],t[1])

    def change_state(self, state):
        self.state = state
        logger.debug("State: " + state,self.name,self.env.now)

    def station_task(self):
        yield self.env.timeout(self.startup_delay) # Starup delay
        logger.info("Starting...",self.name,self.env.now)
        while True:
            if self.part_exists():
                self.change_state("loaded")
                while self.robot_prox == True:
                    yield self.env.timeout(0.10)
                self.change_state("processing")
                yield self.env.timeout(self.yield_timeout(self.process_time))
                self.change_state("finished")
                while self.part_exists():
                    yield self.env.timeout(0.10)
                self.change_state("unloaded")
            yield self.env.timeout(0.10)
