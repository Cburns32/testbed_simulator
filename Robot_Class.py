
class Robot(object):
    def __init__(self, env, name, s1):
        self.env = env
        self.name = name
        self.handoff = False
        self.part_store = simpy.Store(env, capacity=1)
        self.s1 = s1
        self.process = env.process(self.robot_task())

    def part_exists(store):
        return len(store.items)

    def robot_task(self):
        global s1
        while True:

            if self.name == "Robot1":
                if (not self.s1.state == "unloaded") and s2.state == "finished" and s3.state == "unloaded":
                    yield env.timeout(1.0)
                    part_transfer(s2_store, r1_store, self.env.now)
                    p(self.name + ": Picked up part " + part_num(r1_store) + " from " + s2.name)
                    yield env.timeout(5.0)
                    self.handoff = True
                    p(self.name + ": Waiting for " + r2.name)
                    while r2.handoff == False:
                        yield env.timeout(0.01)
                    p(self.name + ": Placed part " + part_num(r2_store) + " in " + r2.name)
                    yield env.timeout(1.0)
                    self.handoff = False
                    link_s1_to_plc.send("Msg")
                elif part_exists(raw_queue) and s1.state == "unloaded":
                    yield env.timeout(1.0)
                    part_transfer(raw_queue, r1_store, self.env.now)
                    p(self.name + ": Picked up part " + part_num(r1_store) + " from queue")
                    yield env.timeout(5.0)
                    part_transfer(r1_store, s1_store, self.env.now)
                    p(self.name + ": Placed part " + part_num(s1_store) + " in " + s1.name)
                    yield env.timeout(1.0)
                elif s1.state == "finished" and s2.state == "unloaded":
                    yield env.timeout(3.0)
                    part_transfer(s1_store, r1_store, self.env.now)
                    p(self.name + ": Picked up part " + part_num(r1_store) + " from " + s1.name)
                    yield env.timeout(2.0)
                    part_transfer(r1_store, s2_store, self.env.now)
                    p(self.name + ": Placed part " + part_num(s2_store) + " in " + s2.name)
                    yield env.timeout(1.0)
            elif self.name == "Robot2":
                if r1.handoff == True and s3.state == "unloaded":
                    yield env.timeout(1.0)
                    part_transfer(r1_store, r2_store, self.env.now)
                    self.handoff = True
                    p(self.name + ": Waiting for " + r1.name + " to release part")
                    while r1.handoff == True:
                        yield env.timeout(0.01)
                    p(self.name + ": Received part " + part_num(r2_store) + " from " + r1.name)
                    yield env.timeout(5.0)
                    part_transfer(r2_store, s3_store, self.env.now)
                    p(self.name + ": Placed part " + part_num(s3_store) + " in " + s3.name)
                    yield env.timeout(1.0)
                    self.handoff = False
                elif s3.state == "finished" and s4.state == "unloaded":
                    yield env.timeout(3.0)
                    part_transfer(s3_store, r2_store, self.env.now)
                    p(self.name + ": Picked up part " + part_num(r2_store) + " from " + s3.name)
                    yield env.timeout(2.0)
                    part_transfer(r2_store, s4_store, self.env.now)
                    p(self.name + ": Placed part " + part_num(s4_store) + " in " + s4.name)
                    yield env.timeout(3.0)
                elif s4.state == "finished":
                    yield env.timeout(3.0)
                    finished_part = part_transfer(s4_store, finished, self.env.now)
                    p(self.name + ": Part " + str(finished_part) + " finished")
                    part_counter.inc()
                    yield env.timeout(2.0)
            yield env.timeout(0.01)
