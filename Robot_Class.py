import simpy, logger, random

class Robot(object):
    def __init__(self, env, name):
        self.env = env
        self.testbed_obj = None
        self.name = name
        self.handoff = False
        self.part_store = simpy.Store(env, capacity=1)
        self.process = env.process(self.robot_task())
        self.link = None
        self.next_job = "None"

    def part_exists(store):
        return len(part_store.items)

    def part_num(self, store):
        return store.items[0].get_id()

    def part_transfer_in(self, from_store):
        part = self.testbed_obj[from_store].part_store.get().value
        part.log_time(self.env.now)
        self.part_store.put(part)

    def part_transfer_out(self, to_store):
        part = self.part_store.get().value
        part.log_time(self.env.now)
        self.testbed_obj[to_store].part_store.put(part)

    def add_link(self, link):
        self.link = link

    def update_testbed(self, objects):
        self.testbed_obj = objects

    def time(self,mu,sigma):
        return random.normalvariate(mu,sigma)

    def robot_task(self):
        logger.info("Starting...",self.name,self.env.now)
        while True:
            self.next_job = None
            #logger.info("Packet status: " + str(self.link.socket_busy("job")) + " " + str(self.link.socket_response("job")),self.name,self.env.now)
            if self.link.socket_busy("job") == False:
                if self.link.socket_response("job") == True:
                    pkt = self.link.get_packet("job")
                    self.next_job = pkt.reply
                    #logger.info("Received job "+str(pkt.reply),self.name,self.env.now)
                    del pkt
                else:
                    self.link.send_packet("job", self.name + "_get_job")

            if self.name == "Robot1":
                if self.next_job == "101":
                    logger.debug("executing job 101",self.name,self.env.now)
                    yield self.env.timeout(self.time(2.598,0.015))              # Move to s2 dwell
                    self.link.send_packet("prox","s2_robot_prox_true")
                    yield self.env.timeout(self.time(2.981,0.007))              # Move to s2 pick, close gripper
                    self.part_transfer_in("s2")
                    yield self.env.timeout(self.time(0.772,0.009))              # Move to s2 dwell
                    self.link.send_packet("prox","s2_robot_prox_false")
                    yield self.env.timeout(self.time(3.406,0.005))              # Move to s7
                    self.handoff = True
                    logger.debug("waiting for Robot2",self.name,self.env.now)
                    while self.testbed_obj["r2"].handoff == False:
                        yield self.env.timeout(0.01)
                    yield self.env.timeout(self.time(4.896,0.023))              # Open gripper, move to candle
                    self.handoff = False

                elif self.next_job == "102":
                    logger.debug("executing job 102",self.name,self.env.now)
                    yield self.env.timeout(self.time(4.907,0.021))              # Move to queue & close gripper
                    self.part_transfer_in("raw_queue")
                    yield self.env.timeout(self.time(4.387,0.023))              # Move to s1 dwell
                    self.link.send_packet("prox","s1_robot_prox_true")
                    yield self.env.timeout(self.time(2.872,0.010))              # Move to s1 pick, open gripper
                    self.part_transfer_out("s1")
                    yield self.env.timeout(self.time(0.782,0.008))              # Move to s1 dwell
                    self.link.send_packet("prox","s1_robot_prox_false")
                    yield self.env.timeout(self.time(1.607,0.009))              # Move to candle
                    logger.debug("completed job 102",self.name,self.env.now)

                elif self.next_job == "103":
                    logger.debug("executing job 103",self.name,self.env.now)
                    yield self.env.timeout(self.time(1.515,0.010))              # Move to s1 dwell
                    self.link.send_packet("prox","s1_robot_prox_true")
                    yield self.env.timeout(self.time(2.970,0.009))              # Move to s1 pick, close gripper
                    self.part_transfer_in("s1")
                    yield self.env.timeout(self.time(0.781,0.008))              # Move to s1 dwell
                    self.link.send_packet("prox","s1_robot_prox_false")
                    yield self.env.timeout(self.time(2.090,0.008))              # Move to s2 dwell
                    self.link.send_packet("prox","s2_robot_prox_true")
                    yield self.env.timeout(self.time(2.974,0.010))              # Move to s2 pick, open gripper
                    self.part_transfer_out("s2")
                    yield self.env.timeout(self.time(0.773,0.010))              # Move to s2 dwell
                    self.link.send_packet("prox","s2_robot_prox_false")
                    yield self.env.timeout(self.time(2.615,0.010))              # Move to candle

            elif self.name == "Robot2":
                if self.next_job == "201":
                    logger.debug("executing job 201",self.name,self.env.now)
                    yield self.env.timeout(self.time(4.789,0.023))              # Move to s8, close gripper
                    self.part_transfer_in("r1")
                    self.handoff = True
                    while self.testbed_obj["r1"].handoff == True:
                        yield self.env.timeout(0.01)
                    yield self.env.timeout(self.time(4.175,0.023))              # Move to s3 dwell *****EDUCATED GUESS*****
                    self.link.send_packet("prox","s3_robot_prox_true")
                    yield self.env.timeout(self.time(3.063,0.007))              # Move to s3 pick, open gripper
                    self.part_transfer_out("s3")
                    yield self.env.timeout(self.time(0.867,0.005))              # Move to s3 dwell
                    self.link.send_packet("prox","s3_robot_prox_false")
                    yield self.env.timeout(self.time(2.443,0.006))              # Move to candle
                    self.handoff = False

                elif self.next_job == "202":
                    logger.debug("executing job 202",self.name,self.env.now)
                    yield self.env.timeout(self.time(2.248,0.006))              # Move to s3 dwell
                    self.link.send_packet("prox","s3_robot_prox_true")
                    yield self.env.timeout(self.time(3.063,0.009))              # Move to s3 pick, close gripper
                    self.part_transfer_in("s3")
                    yield self.env.timeout(self.time(0.867,0.004))              # Move to s3 dwell
                    self.link.send_packet("prox","s3_robot_prox_false")
                    yield self.env.timeout(self.time(1.367,0.005))              # Move to s4 dwell
                    self.link.send_packet("prox","s4_robot_prox_true")
                    yield self.env.timeout(self.time(2.980,0.010))              # Move to s4 pick, open gripper
                    self.part_transfer_out("s4")
                    yield self.env.timeout(self.time(0.789,0.008))              # Move to s4 dwell
                    self.link.send_packet("prox","s4_robot_prox_false")
                    yield self.env.timeout(self.time(2.002,0.004))              # Move to candle

                elif self.next_job == "203":
                    logger.debug("executing job 203",self.name,self.env.now)
                    yield self.env.timeout(self.time(1.807,0.005))              # Move to s4 dwell
                    self.link.send_packet("prox","s4_robot_prox_true")
                    yield self.env.timeout(self.time(2.983,0.010))              # Move to s4 pick, close gripper
                    self.part_transfer_in("s4")
                    yield self.env.timeout(self.time(0.789,0.007))              # Move to s4 dwell
                    self.link.send_packet("prox","s4_robot_prox_false")
                    yield self.env.timeout(self.time(4.742,0.012))              # Move to s5 pick, open gripper
                    self.part_transfer_out("finished")
                    yield self.env.timeout(self.time(2.279,0.014))              # Move to candle

            yield self.env.timeout(0.01)
