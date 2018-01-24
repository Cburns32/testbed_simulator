#!/usr/bin/python
#
# Author: Timothy Zimmerman (timothy.zimmerman@nist.gov)
# Organization: National Institute of Standards and Technology
# U.S. Department of Commerce
# License: Public Domain
#
# See README for description and information
#
# TODO Create CONFIGURATION module for automatically running experiments based
#      on the information provided in a config file, or CLI args
# TODO Create a NETWORKING module that simulates the effects of network performance
#      impacts, and allows each class to communicate.

import simpy, random, sys, stats, time
import logging as log
import logger
from Robot_Class            import Robot
from PLC_Class              import PLC
from Link_Class             import Link
from Station_Class          import Station
from Queue_Class            import Queue
from FinishedParts_Class    import FinishedParts

# Create the logger and set the level
log.getLogger("ts")
log.basicConfig(level=log.WARN)

# Function used to distribute the startup time of each station between min
# and max. Returns an array startup delays of size n.
def random_startup_t(min,max,n):
    t = []
    for i in range(0,n):
        t.append(random.uniform(min,max))
    if n == 1:
        return t[0]
    return t

# Main loop. ITERATIONS defines how many experiments we want to run. Each
# iteration of the FOR loop creates a new experiment.
ITERATIONS = 5
for i in range(0,ITERATIONS):

    start_time = time.time() # Log the wall clock time for logging purposes
    experiment_counter = 10 # Amount of parts to be created in an experiment batch
    random.seed(random.random()) # Randomize the random seed

    env = simpy.Environment()   # Create the simpy environment

    logger.info("Configuring simulation","main", env.now)

    # Instantiate the raw parts queue object
    raw_queue = Queue(env, "raw_queue")

    # Instantiate the finished parts object
    finished_parts = FinishedParts(env, "finished_parts", experiment_counter)

    # Instantiate the PLC object
    plc = PLC(env, raw_queue)

    # Randomize the startup delay
    #startup_t = random_startup_t(0.0,0.100,4)

    # Instantiate the Station 1 object
    s1  = Station(env,"Station1", [5.0,0.01], 0.0)
    # Connect the network links between the station and PLC
    # TODO Replace with a connection request to the NETWORKING module
    plc.add_link(Link(env, "s1", s1, ["station_status","prox"]))

    # Instantiate the Station 2 object
    s2  = Station(env,"Station2", [5.0,0.01], 0.0)
    # Connect the network links between the station and PLC
    plc.add_link(Link(env, "s2", s2, ["station_status","prox"]))

    # Instantiate the Station 3 object
    s3  = Station(env,"Station3", [3.0,0.01], 0.0)
    # Connect the network links between the station and PLC
    plc.add_link(Link(env, "s3", s3, ["station_status","prox"]))

    # Instantiate the Station 4 object
    s4  = Station(env,"Station4", [3.0,0.01], 0.0)
    # Connect the network links between the station and PLC
    plc.add_link(Link(env, "s4", s4, ["station_status","prox"]))

    # Instantiate the Robot 1 object
    r1 = Robot(env,"Robot1")
    # Connect the network links between the robot and PLC
    r1.add_link(Link(env, "r1_plc", plc, ["job","prox"]))

    # Instantiate the Robot 2 object
    r2 = Robot(env,"Robot2")
    # Connect the network links between the robot and PLC
    r2.add_link(Link(env, "r2_plc", plc, ["job","prox"]))

    # Create a dictionary of objects and push to the PLC, Robot 1, and Robot 2 objects.
    # These let the objects gather data from other objects. Will likely be removed
    # once the NETWORKING module is implemented.
    testbed_objects = { "raw_queue":raw_queue, "s1":s1, "s2":s2, "s3":s3, "s4":s4, "r1":r1, "r2":r2, "finished":finished_parts}
    plc.update_testbed(testbed_objects)
    r1.update_testbed(testbed_objects)
    r2.update_testbed(testbed_objects)

    logger.info("Applying configuration file to simulation objects","main", env.now)

    # TODO This is where we apply those configuration parameters...

    logger.info("Starting simulation process","main", env.now)

    # Execute the simulation until the FINISHED PARTS process ends
    env.run(until=finished_parts.process)

    logger.info("Simulation complete","main", env.now)

    # This section is used to print out any relevant data from the simulation.
    # TODO Formalize a output structure containing all of the data we want. Would
    #      probably be a good idea to structure output data exactly as implemented
    #      on the real testbed so the same MATLAB scripts/reports can be utilized.

    #print "Simulation completed in {:.1f} seconds".format(time.time() - start_time)
    #print "Finished parts: " + finished_parts.amount()
    #delim = ","
    #print str(startup_t[0]) + delim + str(startup_t[1]) + delim + str(startup_t[2]) + delim + str(startup_t[3]) + delim + finished_parts.pph()
    #print "{:.3f},{:.3f},{:.3f},{:.3f},".format(s1.startup_delay,s2.startup_delay,s3.startup_delay,s4.startup_delay) + finished_parts.tpp()
    print finished_parts.tpp() # Print the mean/stddev of KPI "time per-part"
