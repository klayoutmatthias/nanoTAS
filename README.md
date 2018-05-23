# nanoTAS
A tiny (hence nano) framework for characterizing stdcells with pyspice

## Description

This experimental framework was created to support logic cell characterisation
with PySpice. It is able to derive timing information for logic gate cells.
It can compute delay and transition times for rising and falling transitions 
with different load capacitances and input slews.

The requirements are:

 * PySpice (https://pyspice.fabrice-salvaire.fr/index.html)
 * Transistor models in a format compatible with ngspice
 * Spice netlists for the gate cells
 * "driver" files which specify the gate ports, the test scenarios and other per-cell parameters
 * A configuration file called "config.py"
 
A sample for the configuration file can be found in `config.py.sample`. Copy the file to
"config.py" and edit it. For details see the comments inside this file.

For the driver files, samples are provided in "drivers-examples".
 
## Basic usage

Check out this script framework somewhere and set the path 
to the directory containing "nanotas.py".

Make sure the "config.py" file is in the current directory.

Run "nanoTAS":

```
nanotas.py
```





