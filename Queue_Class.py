import simpy, logger
from Part_Class import Part

class Queue(object):
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.part_counter = 0
        self.part_store = simpy.Store(env, capacity=1)
        self.process = self.env.process(self.queue_task())

    def part_num(self,store):
        return str(self.part_store.items[0].get_id())

    def part_available(self):
        if len(self.part_store.items) > 0:
            return True
        return False

    def queue_task(self):
        while True:
            if len(self.part_store.items) == 0:
                self.part_counter += 1
                self.part_store.put(Part(self.part_counter, self.env.now))
                logger.debug("Created part: " + self.part_num(self.part_store),self.name,self.env.now)
            yield self.env.timeout(1.0)
