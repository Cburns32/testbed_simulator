
# Author: Timothy Zimmerman (timothy.zimmerman@nist.gov)
# Organization: National Institute of Standards and Technology
# U.S. Department of Commerce
# License: Public Domain
#
# Emulates the behavior and logic of the CSMS Testbed PLC. The PLC handles
# dissemination of jobs to the robots, and is a proxy for informing a station
# if a robot is currently within its operating area. Job dissemination is handled
# by logic that monitors the status of each machining station, and updates the
# job accordingly.

import logger

class PLC(object):
    def __init__(self, env, queue):
        self.env = env # Store a local reference to the simpy environment
        self.links = [] # Array of Link objects
        self.station_status = {} # Dictionary containing the operating status of each station
        self.queue = queue # Local reference to the queue
        self.name = "PLC"
        self.r1_job = "None" # Job number Robot 1 should be executing
        self.r2_job = "None" # Job number Robot 2 should be executing
        self.s1_prox = False # Status of robot proximity at Station 1
        self.s2_prox = False # Status of robot proximity at Station 2
        self.s3_prox = False # Status of robot proximity at Station 3
        self.s4_prox = False # Status of robot proximity at Station 4
        # Create the PLC process in the simpy environment
        self.process = self.env.process(self.plc_task())

    # Called by parent object to create a network link to another testbed object
    def add_link(self, link):
        self.links.append(link)
        self.station_status.update({link.name : "None"})

    # Convenience function that returns the status of a station with name 'name'
    def station(self, name):
        return self.station_status[name]

    # Stores local references to other objects in the testbed for simple data
    # retrieval. Retrieving data for some manufacturing operations is more-easily
    # handled by directly requesting the object data rather than going through the
    # network links, and does not affect the simulator performance.
    def update_testbed(self, objects):
        self.testbed_obj = objects

    # Updates the robot proximity status on a machining station. This is performed
    # using the 'prox' socket preconfigured on the link to the destination station.
    # Ignores the update if the prox message was already sent.
    def prox_update(self, l, prox_value, last_prox):
        if prox_value != last_prox and l.socket_busy("prox") == False:
            last_prox = prox_value
            if prox_value == True:
                l.send_packet("prox","set_prox_true")
                #logger.debug("set prox",self.name,self.env.now)
            else:
                l.send_packet("prox","set_prox_false")
                #logger.debug("clear prox",self.name,self.env.now)
        return last_prox

    # Simpy process for the PLC object. Executes at a 100 Hz rate. Gathers the
    # status for each station, and uses the responses to determine the job for
    # each robot.
    def plc_task(self):
        logger.info("Starting...",self.name,self.env.now)
        # Initialize the proximity variables
        last_s1_prox = False
        last_s2_prox = False
        last_s3_prox = False
        last_s4_prox = False

        # Process loop
        while True:
            # Iterate through each link to obtain the current station status.
            # TODO: This should probably be rewritten as a function (see: prox_update)
            # NOTE: Each link to a station has two sockets:
            #   "station_status" : Station State Messages
            #   "prox"           : Robot Prox Messages
            for link in self.links:
                # Only continue if the station status is busy (has a packet)
                if not link.socket_busy("station_status"):
                    # Test if we received a response; else break
                    if link.socket_response("station_status"):
                        # Store a local reference to the packet
                        pkt = link.get_packet("station_status")
                        #print link.name + " " + str(pkt.reply)
                        # Update the dictionary station entry with the updated status
                        self.station_status.update({link.name : pkt.reply})
                        #print self.station_status
                    else:
                        # The link isn't busy, so send a new request
                        link.send_packet("station_status","get_mbtcp")

                # Since we are iterating through the links, take this opportunity
                # to update the proximity status on each station.
                if link.name == "s1":
                    last_s1_prox = self.prox_update(link, self.s1_prox, last_s1_prox)
                elif link.name == "s2":
                    last_s2_prox = self.prox_update(link, self.s2_prox, last_s2_prox)
                elif link.name == "s3":
                    last_s3_prox = self.prox_update(link, self.s3_prox, last_s3_prox)
                elif link.name == "s4":
                    last_s4_prox = self.prox_update(link, self.s4_prox, last_s4_prox)

            # DO NOT MODIFY! -- Robot 1 logic, as exists within the testbed PLC
            if (not self.station("s1") == "unloaded") and self.station("s2") == "finished" and self.station("s3") == "unloaded":
                self.r1_job = "101"
                #logger.info("Robot job 101",self.name,self.env.now)
            elif self.queue.part_available() and self.station("s1") == "unloaded":
                self.r1_job = "102"
                #logger.info("Robot job 102",self.name,self.env.now)
            elif self.station("s1") == "finished" and self.station("s2") == "unloaded":
                self.r1_job = "103"
                #logger.info("Robot job 103",self.name,self.env.now)
            else:
                self.r1_job = "None"


            # DO NOT MODIFY! -- Robot 2 logic, as exists within the testbed PLC
            if self.testbed_obj["r1"].handoff == True and self.station("s3") == "unloaded":
                self.r2_job = "201"
                #logger.info("Robot job 201",self.name,self.env.now)
            elif self.station("s3") == "finished" and self.station("s4") == "unloaded":
                self.r2_job = "202"
                #logger.info("Robot job 202",self.name,self.env.now)
            elif self.station("s4") == "finished":
                self.r2_job = "203"
                #logger.info("Robot job 203",self.name,self.env.now)
            else:
                self.r2_job = "None"

            # Yield the PLC process until the next scheduled iteration (100 Hz)
            # TODO: Make this a configurable value
            yield self.env.timeout(0.01)
