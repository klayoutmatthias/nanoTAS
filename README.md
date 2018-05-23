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

## Details about the implementation

The implementation is based on PySpice which is a Python library wrapping
libngspice ("shared ngspice") and combining it with NumPy. In effect this 
is a very convenient framework for running mass simulations on synthetic
spice netlists and combining them with automated analysis. For details about 
the PySpice API see https://pyspice.fabrice-salvaire.fr/overview.html.

nanoTAS implements a context class collecting the setup from the driver
files. Technically the driver files are Python scripts executed in the
context of this object. Upon "collect", PySpice is used to prepare a
netlist for each inslew/capa load pair with the stimulus pulse, the DC 
power source, dummy loads for ngspice convergence and the capacitance loads.

After this, the simulation is started using the time interval and time 
resolution provided by the config file.

The collected waveforms are analysed to get the measurements:

 * Input pin capacitances are computed by integrating over the 
   input pin current (charge Q) and using `C = Q/U`.
 * The energy per transition is computed by integrating the power supply 
   current (Q) and using the energy equation: `E = Q*U`.
 * The rise and fall times are computed as the time difference between the
   10% and 90% levels.
 * The delay times are measured between the 50% transitions of input and
   output.
   
## TODO

 * Simplify the production of driver files
 * Support for hold/setup time extraction for latches and FF's
 * Generation of .lib files




