# Testbed Simulator
This Python project simulates the discrete events that occur within the Cybersecurity for NIST Smart Manufacturing Systems Testbed, located at the National Institute of Standards and Technology in Gaithersburg, Maryland. The Robotic System of the testbed (which this simulator models) utilizes two KUKA Youbots and four emulated machining centers. Machine tending is handled by the robots, transferring parts from station to station until all manufacturing operations are completed.

This simulator breaks down testbed operations into discrete events, which are handled by the SimPy simulation framework. The operations of each system component are modeled in Python to closely reproduce their unique characteristics. Robot movements were discretized through time domain measurements, and are reproduced in the simulator using normal variate distributions.

## Dependencies
As of this moment, the simulator is running with the following dependencies:
* Python 2.7.12
* SimPy 3.0.7
* NumPy 1.11.0
* Matplotlib 1.5.1

## Running the simulator
The simulation is executed by the file ```sim.py```. Make sure this file is executable, and execute it from the command line. Future versions will likely include command line arguments, but at this point there are none.

## Further Reading
* [NIST Cybersecurity for Smart Manufacturing Systems Project Description][_CSMS]
* [NIST IR 8177 - Metrics and Key Performance Indicators for Robotic Cybersecurity Performance Analysis][_IR8177]
* [NIST IR 8089 - An Industrial Control System Cybersecurity Performance Testbed][_IR8089]

## Contact
Questions, concerns, and feedback regarding this project should be addressed
to timothy.zimmerman@nist.gov (Timothy Zimmerman), or [filed as an issue][_issues].

## Disclaimer
Certain commercial entities, equipment, or materials may be identified in this
document in order to describe an experimental procedure or concept adequately.
Such identification is not intended to imply recommendation or endorsement by
the [National Institute of Standards and Technology (NIST)][_NIST], nor is it
intended to imply that the entities, materials, or equipment are necessarily
the best available for the purpose.

[_NIST]: http://www.nist.gov
[_issues]: https://github.com/timzim-nist/testbed_simulator/issues
[_IR8089]: http://nvlpubs.nist.gov/nistpubs/ir/2015/NIST.IR.8089.pdf
[_IR8177]: http://nvlpubs.nist.gov/nistpubs/ir/2017/NIST.IR.8177.pdf
[_CSMS]: https://www.nist.gov/programs-projects/cybersecurity-smart-manufacturing-systems
