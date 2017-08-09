import logging

logger = logging.getLogger("ts")

def debug(msg,n,t):
    logger.debug("[" + "{:.3f}".format(t) + "] [" + n + "] " + msg)

def info(msg,n,t):
    logger.info("[" + "{:.3f}".format(t) + "] [" + n + "] " + msg)

def warn(msg,n,t):
    logger.warn("[" + "{:.3f}".format(t) + "] [" + n + "] " + msg)
