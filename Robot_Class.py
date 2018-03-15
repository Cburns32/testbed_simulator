
# Author: Timothy Zimmerman (timothy.zimmerman@nist.gov)
# Organization: National Institute of Standards and Technology
# U.S. Department of Commerce
# License: Public Domain
#
# Models the behavior of the robotic arms, per measurements obtained from the
# CSMS Testbed (see ./timing_analysis/).

import simpy, logger, random

class Robot(object):
    def __init__(self, env, name):
        self.env = env # Store a local reference to the simpy environment
        self.testbed_obj = None
        self.name = name
        self.handoff = False # Variable for coordinating handoff between R1 and R2
        self.part_store = simpy.Store(env, capacity=1) # Robot can hold 1 part
        self.link = None # Robot has a single link (Robot-to-PLC)
        self.next_job = "None" # Local variable of the next job (from PLC)
        # Create the Robot process in the simpy environment
        self.process = self.env.process(self.robot_task())

    # Returns if robot has part
    def part_exists(store):
        return len(part_store.items)

    # Returns ID of part in store
    def part_num(self, store):
        return store.items[0].get_id()

    # Transfers a part from the "from_store" object reference to the local store
    def part_transfer_in(self, from_store):
        # Store a local reference to the part (remove part from "from_store")
        part = self.testbed_obj[from_store].part_store.get().value
        part.log_time(self.env.now) # Trigger the part to store the current timestamp
        self.part_store.put(part) # Put the part in the local store

    # Transfers a part from the local store to the "to_store" object reference
    def part_transfer_out(self, to_store):
        part = self.part_store.get().value # Pull the part out of the local store
        part.log_time(self.env.now) # Trigger the part to store the current timestamp
        self.testbed_obj[to_store].part_store.put(part) # Put part in "to_store" object's store

    # Called by parent object to create a network link to another testbed object.
    # NOTE The robot only has ONE link
    def add_link(self, link):
        self.link = link

    # Stores local references to other objects in the testbed for simple data
    # retrieval. This is especially important for the transfering of part objects
    # between testbed objects (see part_transfer_in and part_transfer_out).
    def update_testbed(self, objects):
        self.testbed_obj = objects

    # Calculates a move execution time based on the normal distribution. Modeled
    # behavior was determined from testing on the CSMS Testbed (see ./timing_analysis/),
    # and is defined by the mean and stddev.
    # https://docs.python.org/2/library/random.html#random.normalvariate
    def time(self,mu,sigma):
        return random.normalvariate(mu,sigma)

    # Simpy process for the Robot object.
    def robot_task(self):
        logger.info("Starting...",self.name,self.env.now)
        while True:
            # Clear the current job, and check to see if we have a new job.
            # This logic is similar in operation to the PLC task.
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

            # DO NOT MODIFY ANY TIMEOUTS IN THIS LOGIC! Everything below this
            # line is modeled from testbed operations. Code related to packet
            # transmissions is fair game for modification; however, the order of
            # operations for each job should NOT be changed.
            #
            # Similar to the testbed, we use a single Class to represent the Robot;
            # therefore we need logic to determine which robot we are so the wrong
            # jobs aren't executed.
            #
            # TODO Add registration function to test for other testbed objects with
            # the same name. Error if true.

            # The following three jobs belong to Robot 1.
            if self.name == "Robot1":
                # JOB 101: Move the part from S2 and handoff to R2
                if self.next_job == "101":
                    logger.debug("executing job 101",self.name,self.env.now)
                    yield self.env.timeout(self.time(2.598,0.015))              # Move to s2 dwell
                    self.link.send_packet("prox","s2_robot_prox_true")          # Update the station's robot proximity status
                    yield self.env.timeout(self.time(2.981,0.007))              # Move to s2 pick, close gripper
                    self.part_transfer_in("s2")                                 # Transfer the part object
                    yield self.env.timeout(self.time(0.772,0.009))              # Move to s2 dwell
                    self.link.send_packet("prox","s2_robot_prox_false")         # Update the station's robot proximity status
                    yield self.env.timeout(self.time(3.406,0.005))              # Move to s7
                    self.handoff = True                                         # Shared variable to denote handoff status between R1 and R2
                    logger.debug("waiting for Robot2",self.name,self.env.now)
                    while self.testbed_obj["r2"].handoff == False:              # Shared variable to denote handoff status between R2 and R1
                        yield self.env.timeout(0.01)                            # Handoff not complete; test again in 10 milliseconds
                    yield self.env.timeout(self.time(4.896,0.023))              # Open gripper, move to candle
                    self.handoff = False                                        # Shared variable to denote handoff status between R1 and R2
                # JOB 102: Move the part in the queue to S1
                elif self.next_job == "102":
                    logger.debug("executing job 102",self.name,self.env.now)
                    yield self.env.timeout(self.time(4.907,0.021))              # Move to queue & close gripper
                    self.part_transfer_in("raw_queue")                          # Transfer the part object
                    yield self.env.timeout(self.time(4.387,0.023))              # Move to s1 dwell
                    self.link.send_packet("prox","s1_robot_prox_true")          # Update the station's robot proximity status
                    yield self.env.timeout(self.time(2.872,0.010))              # Move to s1 pick, open gripper
                    self.part_transfer_out("s1")                                # Transfer the part object
                    yield self.env.timeout(self.time(0.782,0.008))              # Move to s1 dwell
                    self.link.send_packet("prox","s1_robot_prox_false")         # Update the station's robot proximity status
                    yield self.env.timeout(self.time(1.607,0.009))              # Move to candle
                    logger.debug("completed job 102",self.name,self.env.now)
                # JOB 103: Move the part from S1 to S2
                elif self.next_job == "103":
                    logger.debug("executing job 103",self.name,self.env.now)
                    yield self.env.timeout(self.time(1.515,0.010))              # Move to s1 dwell
                    self.link.send_packet("prox","s1_robot_prox_true")          # Update the station's robot proximity status
                    yield self.env.timeout(self.time(2.970,0.009))              # Move to s1 pick, close gripper
                    self.part_transfer_in("s1")                                 # Transfer the part object
                    yield self.env.timeout(self.time(0.781,0.008))              # Move to s1 dwell
                    self.link.send_packet("prox","s1_robot_prox_false")         # Update the station's robot proximity status
                    yield self.env.timeout(self.time(2.090,0.008))              # Move to s2 dwell
                    self.link.send_packet("prox","s2_robot_prox_true")          # Update the station's robot proximity status
                    yield self.env.timeout(self.time(2.974,0.010))              # Move to s2 pick, open gripper
                    self.part_transfer_out("s2")                                # Transfer the part object
                    yield self.env.timeout(self.time(0.773,0.010))              # Move to s2 dwell
                    self.link.send_packet("prox","s2_robot_prox_false")         # Update the station's robot proximity status
                    yield self.env.timeout(self.time(2.615,0.010))              # Move to candle

            # The following three jobs belong to Robot 2
            elif self.name == "Robot2":
                # JOB 201: Move the part from the handoff to S3
                if self.next_job == "201":
                    logger.debug("executing job 201",self.name,self.env.now)
                    yield self.env.timeout(self.time(4.789,0.023))              # Move to s8, close gripper
                    self.part_transfer_in("r1")                                 # Transfer the part object
                    self.handoff = True                                         # Shared variable to denote handoff status between R2 and R1
                    while self.testbed_obj["r1"].handoff == True:               # Shared variable to denote handoff status between R1 and R2
                        yield self.env.timeout(0.01)                            # Handoff not complete; test again in 10 milliseconds
                    yield self.env.timeout(self.time(4.175,0.023))              # Move to s3 dwell *****EDUCATED GUESS*****
                    self.link.send_packet("prox","s3_robot_prox_true")          # Update the station's robot proximity status
                    yield self.env.timeout(self.time(3.063,0.007))              # Move to s3 pick, open gripper
                    self.part_transfer_out("s3")                                # Transfer the part object
                    yield self.env.timeout(self.time(0.867,0.005))              # Move to s3 dwell
                    self.link.send_packet("prox","s3_robot_prox_false")         # Update the station's robot proximity status
                    yield self.env.timeout(self.time(2.443,0.006))              # Move to candle
                    self.handoff = False                                        # Shared variable to denote handoff status between R2 and R1
                # JOB 202: Move the part from S3 to S4
                elif self.next_job == "202":
                    logger.debug("executing job 202",self.name,self.env.now)
                    yield self.env.timeout(self.time(2.248,0.006))              # Move to s3 dwell
                    self.link.send_packet("prox","s3_robot_prox_true")          # Update the station's robot proximity status
                    yield self.env.timeout(self.time(3.063,0.009))              # Move to s3 pick, close gripper
                    self.part_transfer_in("s3")                                 # Transfer the part object
                    yield self.env.timeout(self.time(0.867,0.004))              # Move to s3 dwell
                    self.link.send_packet("prox","s3_robot_prox_false")         # Update the station's robot proximity status
                    yield self.env.timeout(self.time(1.367,0.005))              # Move to s4 dwell
                    self.link.send_packet("prox","s4_robot_prox_true")          # Update the station's robot proximity status
                    yield self.env.timeout(self.time(2.980,0.010))              # Move to s4 pick, open gripper
                    self.part_transfer_out("s4")                                # Transfer the part object
                    yield self.env.timeout(self.time(0.789,0.008))              # Move to s4 dwell
                    self.link.send_packet("prox","s4_robot_prox_false")         # Update the station's robot proximity status
                    yield self.env.timeout(self.time(2.002,0.004))              # Move to candle
                # JOB 203: Move the part from S4 to the finished parts 'bin'
                elif self.next_job == "203":
                    logger.debug("executing job 203",self.name,self.env.now)
                    yield self.env.timeout(self.time(1.807,0.005))              # Move to s4 dwell
                    self.link.send_packet("prox","s4_robot_prox_true")          # Update the station's robot proximity status
                    yield self.env.timeout(self.time(2.983,0.010))              # Move to s4 pick, close gripper
                    self.part_transfer_in("s4")                                 # Transfer the part object
                    yield self.env.timeout(self.time(0.789,0.007))              # Move to s4 dwell
                    self.link.send_packet("prox","s4_robot_prox_false")         # Update the station's robot proximity status
                    yield self.env.timeout(self.time(4.742,0.012))              # Move to s5 pick, open gripper
                    self.part_transfer_out("finished")                          # Transfer the part object
                    yield self.env.timeout(self.time(2.279,0.014))              # Move to candle

            # We don't currently have a job, so check again in 10 milliseconds
            yield self.env.timeout(0.01)
