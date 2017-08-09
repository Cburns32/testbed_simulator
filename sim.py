#!/usr/bin/python

import simpy, random, sys, stats, time
import logging as log
import logger
from Robot_Class            import Robot
from PLC_Class              import PLC
from Link_Class             import Link
from Station_Class          import Station
from Queue_Class            import Queue
from FinishedParts_Class    import FinishedParts

log.getLogger("ts")
log.basicConfig(level=log.WARN)

def random_startup_t(min,max,n):
    t = []
    for i in range(0,n):
        t.append(random.uniform(min,max))
    if n == 1:
        return t[0]
    return t

ITERATIONS = 5
for i in range(0,ITERATIONS):

    start_time = time.time()
    experiment_counter = 10
    random.seed(random.random())
    env = simpy.Environment()
    logger.info("Configuring simulation","main", env.now)
    raw_queue = Queue(env, "raw_queue")
    finished_parts = FinishedParts(env, "finished_parts", experiment_counter)
    plc = PLC(env, raw_queue)
    #startup_t = random_startup_t(0.0,0.100,4)

    s1  = Station(env,"Station1", [5.0,0.01], 0.0)
    plc.add_link(Link(env, "s1", s1, ["station_status","prox"]))

    s2  = Station(env,"Station2", [5.0,0.01], 0.0)
    plc.add_link(Link(env, "s2", s2, ["station_status","prox"]))

    s3  = Station(env,"Station3", [3.0,0.01], 0.0)
    plc.add_link(Link(env, "s3", s3, ["station_status","prox"]))

    s4  = Station(env,"Station4", [3.0,0.01], 0.0)
    plc.add_link(Link(env, "s4", s4, ["station_status","prox"]))

    r1 = Robot(env,"Robot1")
    r1.add_link(Link(env, "r1_plc", plc, ["job","prox"]))

    r2 = Robot(env,"Robot2")
    r2.add_link(Link(env, "r2_plc", plc, ["job","prox"]))

    testbed_objects = { "raw_queue":raw_queue, "s1":s1, "s2":s2, "s3":s3, "s4":s4, "r1":r1, "r2":r2, "finished":finished_parts}
    plc.update_testbed(testbed_objects)
    r1.update_testbed(testbed_objects)
    r2.update_testbed(testbed_objects)

    logger.info("Applying configuration file to simulation objects","main", env.now)
    # This is where we apply those config file parameters...

    logger.info("Starting simulation process","main", env.now)
    env.run(until=finished_parts.process)
    #env.run(until=200.0)

    logger.info("Simulation complete","main", env.now)
    #print "Simulation completed in {:.1f} seconds".format(time.time() - start_time)
    #print "Finished parts: " + finished_parts.amount()
    #delim = ","
    #print str(startup_t[0]) + delim + str(startup_t[1]) + delim + str(startup_t[2]) + delim + str(startup_t[3]) + delim + finished_parts.pph()
    #print "{:.3f},{:.3f},{:.3f},{:.3f},".format(s1.startup_delay,s2.startup_delay,s3.startup_delay,s4.startup_delay) + finished_parts.tpp()
    print finished_parts.tpp()
