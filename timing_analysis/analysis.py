#!/usr/bin/python

import numpy

results = open("results.csv", "w")
results.write("job,task,hint,mean,std\n")

for log in ["./robot1.log","./robot2.log"]:
    f = open(log,"r")

    last_job = 0
    job_step_counter = 0
    delim = ","

    moves_dict = {"101":{}, "102":{}, "103":{}, "201":{}, "202":{}, "203":{}}
    moves_hints = {"101":{}, "102":{}, "103":{}, "201":{}, "202":{}, "203":{}}

    for l in f:
        if l[37:38] == "1" or l[37:38] == "2":
            task = l[37:].split(delim)
            if task[0] != last_job:
                last_job = task[0]
                job_step_counter = 0
            if not job_step_counter in moves_dict[task[0]]:
                moves_dict[task[0]][job_step_counter] = []
            moves_dict[task[0]][job_step_counter].append(float(task[2]))
            moves_hints[task[0]][job_step_counter] = task[1]
            job_step_counter += 1

    for job in moves_dict:
        for task in moves_dict[job]:
            results.write(str(job) + delim + str(task) + delim + moves_hints[job][task] + delim + "{:.3f}".format(numpy.mean(moves_dict[job][task])) + delim + "{:.3f}".format(numpy.std(moves_dict[job][task])) + "\n")

    f.close()
results.close()
