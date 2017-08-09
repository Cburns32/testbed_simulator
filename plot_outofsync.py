#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

# baseline = open("./baseline.csv")
# baseline_data = []
# for line in baseline:
#     d = line.split(",")
#     baseline_data.append(float(d[4]))
# baseline.close()

test = open("s1_outofsync.csv")
test_t     = []
test_std   = []
test_delay = []
for line in test:
    l = line.split(",")
    test_delay.append(float(l[0]))
    test_t.append(float(l[4]))
    test_std.append(float(l[5]))
test.close()

plt.figure()
#plt.boxplot(data)
plt.subplot(1,2,1)
plt.scatter(test_delay, test_t)
plt.subplot(1,2,2)
plt.scatter(test_delay, test_std)
plt.show()
