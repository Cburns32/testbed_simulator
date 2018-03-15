
# Author: Timothy Zimmerman (timothy.zimmerman@nist.gov)
# Organization: National Institute of Standards and Technology
# U.S. Department of Commerce
# License: Public Domain
#
# Object used to represent a "part" in the testbed. The object is passed between
# virtual testbed components as it travels through the manufacturing process.
# This object also tracks the timestamps for each transition during the process
# (e.g., queue-to-Robot1 pickup, Robot1-to-Station1 dropoff). Having the part
# represented as an object allows us to implement many cool features, however,
# the features are limited at this time.
#
# A unique part object exists for every part created by the virtual testbed. These
# objects are collected by the FinishedParts_Class after Station 4.

class Part(object):
    def __init__(self, part_id, t):
        self.id = part_id
        self.tracker_array = [] # Array to hold event timestamps

    # Convenience function; returns the part number (id)
    def get_id(self):
        return self.id

    # Function to append a new event timestamp to the tracker_array. Called by
    # the testbed object performing the 'transfer'
    def log_time(self, t):
        self.tracker_array.append("{:.3f}".format(t))

    # Returns a string of the part event timestamps.
    # TODO: Clean up this mess...
    def log(self):
        d = ","
        t = self.tracker_array
        return str(self.id) +d+"2"+d+ str(t[2]) +d+ str(t[3]) +d+ str(t[4]) +d+ str(t[5]) +d+ str(t[6]) +d+ str(t[7]) +d+ str(t[8]) +d+ str(t[9]) +d+ str(t[0]) +d+ str(t[1])
