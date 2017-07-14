#!/usr/bin/python

import simpy, random, sys, stats
import logging as log
from Robot_Class   import Robot
from PLC_Class     import PLC
from Link_Class    import Link
from Station_Class import Station

def part_num(store):
    return str(store.items[0].get_id())

def part_log_time(store,t):
    store.items[0].log_time(t)

def part_transfer(from_store, to_store, t):
    part = from_store.get().value
    part.log_time(t)
    to_store.put(part)
    return part.get_id()

def p(msg):
    log.debug("[" + "{:8.3f}".format(env.now) + "] " + msg)


class Part_Counter(object):
    def __init__(self):
        self.count = 0
    def inc(self):
        self.count += 1
    def value(self):
        return self.count

class Part():
    def __init__(self, part_id):
        self.id = part_id
        self.tracker_array = []
    def get_id(self):
        return self.id
    def log_time(self,t):
        self.tracker_array.append(t)


def queue(env):
    global queue_ctr
    while True:
        if len(raw_queue.items) == 0:
            queue_ctr = queue_ctr + 1
            raw_queue.put(Part(queue_ctr))
            p("Queue: " + part_num(raw_queue))
        yield env.timeout(1.0)


def experiment_tracker():
    while True:
        if part_counter.value() >= experiment_counter:
            log.info("[DONE]")
            stats.compute_stats(finished)
            env.exit()
        yield env.timeout(1.0)

log.getLogger()
log.basicConfig(level=log.ERROR)
ITERATIONS = 1
# for i in range(0,ITERATIONS):

queue_ctr = 0
experiment_counter = 10
log.info("[CONFIGURING SIMULATION]")

random.seed(random.random())

env = simpy.Environment()

# All testbed components "store" a part (temporarily), so create a Store
# for each station/robot/queue
raw_queue = simpy.Store(env, capacity=1)
finished  = simpy.Store(env)

s1  = Station(env,"Station1", 5.0, 0.1)
s2  = Station(env,"Station2", 4.0, 0.1)
s3  = Station(env,"Station3", 3.0, 0.1)
s4  = Station(env,"Station4", 3.0, 0.1)
plc = PLC(env)

plc_to_s1_link = Link(env, "plc_to_s1", plc, s1)
plc_to_s2_link = Link(env, "plc_to_s2", plc, s2)
plc_to_s3_link = Link(env, "plc_to_s3", plc, s3)
plc_to_s4_link = Link(env, "plc_to_s4", plc, s4)

plc.add_link(plc_to_s1_link)
plc.add_link(plc_to_s2_link)
plc.add_link(plc_to_s3_link)
plc.add_link(plc_to_s4_link)




# r1 = Robot(env,"Robot1", s1)
# r2 = Robot(env,"Robot2", s1)

part_counter = Part_Counter()
tracker = env.process(experiment_tracker())

env.process(queue(env))

log.info("[STARTING SIMULATION]")
#env.run(until=tracker)
env.run(until=1.0)
