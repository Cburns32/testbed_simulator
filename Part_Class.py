

class Part(object):
    def __init__(self, part_id, t):
        self.id = part_id
        self.tracker_array = []

    def get_id(self):
        return self.id

    def log_time(self, t):
        self.tracker_array.append("{:.3f}".format(t))

    def log(self):
        d = ","
        t = self.tracker_array
        return str(self.id) +d+"2"+d+ str(t[2]) +d+ str(t[3]) +d+ str(t[4]) +d+ str(t[5]) +d+ str(t[6]) +d+ str(t[7]) +d+ str(t[8]) +d+ str(t[9]) +d+ str(t[0]) +d+ str(t[1])
