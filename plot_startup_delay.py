#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

baseline = open("./baseline.csv")
baseline_data = []
for line in baseline:
    d = line.split(",")
    baseline_data.append(float(d[4]))
baseline.close()

delay = open("startup_delay.csv")
delay_data = []
for line in delay:
    d = line.split(",")
    delay_data.append(float(d[4]))
delay.close()

print "Baseline: \t {:.2f} +/- {:.2f}  Min: {:.2f}  Max: {:.2f}".format(np.mean(baseline_data),np.std(baseline_data),np.min(baseline_data),np.max(baseline_data))
print "Delay: \t\t {:.2f} +/- {:.2f}  Min: {:.2f}  Max: {:.2f}".format(np.mean(delay_data),np.std(delay_data),np.min(delay_data),np.max(delay_data))

data = [baseline_data, delay_data]
plt.figure()
#plt.boxplot(data)
plt.hist(data)
plt.show()
