import logger

class PLC(object):
    def __init__(self, env, queue):
        self.env = env
        self.links = []
        self.station_status = {}
        self.queue = queue
        self.name = "PLC"
        self.r1_job = "None"
        self.r2_job = "None"
        self.s1_prox = False
        self.s2_prox = False
        self.s3_prox = False
        self.s4_prox = False
        self.process = self.env.process(self.plc_task())

    def add_link(self, link):
        self.links.append(link)
        self.station_status.update({link.name : "None"})

    def tx(self, link, msg):
        self.links[link].tx(msg)

    def station(self, name):
        return self.station_status[name]

    def update_testbed(self, objects):
        self.testbed_obj = objects

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

    def plc_task(self):
        logger.info("Starting...",self.name,self.env.now)
        last_s1_prox = False
        last_s2_prox = False
        last_s3_prox = False
        last_s4_prox = False

        # station_pkt = link.tx("get_mbtcp")
        # self.station_status.update({link.name : station_pkt.reply})

        while True:
            # Each link to a station has two sockets:
            #   "station_status" : Station State Messages
            #   "prox"           : Robot Prox Messages
            for link in self.links:
                if not link.socket_busy("station_status"):
                    if link.socket_response("station_status"):
                        pkt = link.get_packet("station_status")
                        #print link.name + " " + str(pkt.reply)
                        self.station_status.update({link.name : pkt.reply})
                        #print self.station_status
                    else:
                        link.send_packet("station_status","get_mbtcp")

                if link.name == "s1":
                    last_s1_prox = self.prox_update(link, self.s1_prox, last_s1_prox)
                elif link.name == "s2":
                    last_s2_prox = self.prox_update(link, self.s2_prox, last_s2_prox)
                elif link.name == "s3":
                    last_s3_prox = self.prox_update(link, self.s3_prox, last_s3_prox)
                elif link.name == "s4":
                    last_s4_prox = self.prox_update(link, self.s4_prox, last_s4_prox)

            # Robot1 Logic
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


            # Robot2 Logic
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


            yield self.env.timeout(0.01)
