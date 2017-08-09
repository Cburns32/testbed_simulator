#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

baseline = open("./baseline_1000.csv")
baseline_data = []
for line in baseline:
    d = line.split(",")
    baseline_data.append(float(d[4]))
baseline.close()

print "Baseline: {:.2f} +/- {:.2f}  Min: {:.2f}  Max: {:.2f}".format(np.mean(baseline_data),np.std(baseline_data),np.min(baseline_data),np.max(baseline_data))


# plt.figure()
# plt.hist(baseline_data)
# plt.show()
