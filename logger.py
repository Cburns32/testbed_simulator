
# Author: Timothy Zimmerman (timothy.zimmerman@nist.gov)
# Organization: National Institute of Standards and Technology
# U.S. Department of Commerce
# License: Public Domain
#
# Logger functions to make life easier. Automatically attaches to the current
# Python logger, and provides simple functions for creating the messages.
#
# msg : Message to be logged
# n   : Name of the object that created the log message
# t   : Simulation time the log message was created

import logging

logger = logging.getLogger("ts")

def debug(msg,n,t):
    logger.debug("[" + "{:.3f}".format(t) + "] [" + n + "] " + msg)

def info(msg,n,t):
    logger.info("[" + "{:.3f}".format(t) + "] [" + n + "] " + msg)

def warn(msg,n,t):
    logger.warn("[" + "{:.3f}".format(t) + "] [" + n + "] " + msg)
