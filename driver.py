

import math
import numpy as np
import scipy.optimize as opt

# for debugging
import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging
# To enable logging:
# logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

import functions
import results

# ------------------------------------------------------------------------------

class Driver(object):

  """ 
  The main simulation driver class

  This class handles the evaluation of the driver.py file and the 
  execution of the simulation.

  Usage is like this:

    import config
    from driver import *

    with open("drivers.py") as file:
      driver = Driver("cellname", config)
      exec(file.read(), globals(), driver.vars)
      driver.results.dump()
  """

  _netlist = None
  _ports = []
  _capa_table = []
  _slew_table = []
  _plot_results = False
  _config = None

  vars = {}
  name = ""
  results = None

  def __init__(self, name, config):

    self._config = config
    self.name = name
    self.results = results.Results(name)

    if "netlist_pattern" in config.__dict__:
      self._netlist = config.netlist_pattern.replace("%name%", name)

    self.vars = {
      "name": name,
      "capa_table": self.capa_table,
      "slew_table": self.slew_table,
      "plot": self.plot,
      "netlist": self.netlist,
      "pins": self.pins,
      "high": functions.High(),
      "low": functions.Low(),
      "pos": functions.PositiveTransition(),
      "neg": functions.NegativeTransition(),
      "edge": functions.Edge(),
      "probe": self.probe,
      "collect": self.collect
    }

    self._capa_table = config.capa_table
    self._slew_table = config.slew_table

    self._plot_results = "plot" in config.__dict__ and config.plot


  def plot(self, p):
    self._plot_results = p


  def slew_table(self, *st):
    self._slew_table = st

    
  def capa_table(self, *ct):
    self._capa_table = ct

    
  def netlist(self, nl):
    self._netlist = nl
      

  def set(self, pin, value):
    self._ports_assigned[pin] = value


  def pins(self, *args):

    self._ports = args
    self._ports_assigned = {}

    gnd_found = False
    power_found = False

    for a in args:
      if a == "power":
        power_found = True
      elif a == "gnd":
        gnd_found = True
      else:
        self.vars[a] = lambda value, pin = a: self.set(pin, value)
        self._ports_assigned[a] = None

    if not power_found:
      raise Exception("pins(): one pin needs to be 'power' for the assignment of supply voltage")
    if not gnd_found:
      raise Exception("pins(): one pin needs to be 'gnd' for the ground connection")


  def probe(self, name):
    return functions.Probe(name)


  def buildCircuit(self, slew, capa, polarity):
    
    print("Building circuit for slew = " + ("%.2f" % slew) + ", capa = " + ("%.2f" % capa))
    circuit = Circuit(self.name)
    circuit.include(self._config.models)
    
    vdd = self._config.nom_voltage

    circuit.VoltageSource("vdd", "power", "gnd", vdd)

    # produce the sources and loads for the pins
    for pin in self._ports_assigned.keys():
      asgn = self._ports_assigned[pin]
      if not asgn:
        raise Exception("Pin '" + pin + "' not assigned a function or signal - use '<pinname>(...)' in the driver file")
      else:
        asgn.makeCircuit(circuit, pin, vdd, slew, capa, self._config, polarity)

    # reference of the cell
    circuit.X("dut", self.name, *self._ports)

    # include the cell to test
    circuit.include(self._netlist)

    return circuit


  def getInput(self, polarity):

    input = None
    for pin in self._ports_assigned.keys():
      asgn = self._ports_assigned[pin]
      if asgn.isInput(polarity):
        if input:
          raise Exception("More than one input specified (" + input + " and " + pin + ")")
        input = pin

    return input
    

  def computeTransition(self, analysis, node, v):
    return opt.bisect(lambda x: np.interp(x, analysis.time, analysis.nodes[node]) - v, 0, self._config.stop@u_ps)

  def computeSlew(self, analysis, node, vmax):
    return abs(self.computeTransition(analysis, node, vmax * 0.9) - self.computeTransition(analysis, node, vmax * 0.1))

  def getProbes(self):

    probes = {}
    for pin in self._ports_assigned.keys():
      asgn = self._ports_assigned[pin]
      if asgn.isOutput():
        probes[pin] = asgn

    if len(probes) == 0:
      raise Exception("No output specified - use '<pinname>(positive)' or '<pinname>(negative)' for at least one pin")
    return probes
    

  def collect(self):

    if not self._netlist:
      raise Exception("Netlist not specified - 'netlist(...)' missing in the driver file?")

    temperature = 25
    if "temperature" in self._config.__dict__:
      temperature = self._config.__dict__["temperature"]

    vcross = self._config.nom_voltage * 0.5
    vdd = self._config.nom_voltage

    # count the simulations for the progress
    simCount = 0

    for polarity in [ True, False ]:
      input = self.getInput(polarity)
      if input:
        simCount += len(self._slew_table) * len(self._capa_table)

    simIndex = 0

    for polarity in [ True, False ]:

      input = self.getInput(polarity)
      if not input:
        continue

      polarityString = { True: "positive", False: "negative" }[polarity]

      for slew in self._slew_table:

        for capa in self._capa_table:

          simIndex += 1
          print("\n(" + str(simIndex) + "/" + str(simCount) + ") Performing analysis for polarity '" + polarityString + "' with C(load)=" + ("%.2f" % capa) + "fF, slew(Input)=" + ("%.2f" % slew) + "ps ...\n")

          circuit = self.buildCircuit(slew, capa, polarity)

          simulator = circuit.simulator(temperature = temperature)
          analysis = simulator.transient(step_time = self._config.step@u_ps, end_time = self._config.stop@u_ps)

          tIn = self.computeTransition(analysis, input, vcross)

          for pin, probe in self.getProbes().items():

            if self._plot_results:
              self.plotResults(analysis, input, pin)

            tOut = self.computeTransition(analysis, pin, vcross)
            
            delay = tOut - tIn
            print("Delay: %.6g ps" % (delay * 1e12))

            transition = self.computeSlew(analysis, pin, vdd)
            print("Slew(output): %.6g ps" % (transition * 1e12))

            charge = np.trapz([ float(x) for x in analysis.branches["vstim_" + input] ], x = [ float(t) for t in analysis.time ])
            print("Input charge: %.6g" % charge) 

            powerCharge = np.trapz([ float(x) for x in analysis.branches["vvdd"] ], x = [ float(t) for t in analysis.time ])
            print("Power charge: %.6g" % powerCharge) 

            ri = self.results.addOutput(pin).addInput(input)
            if ri.inputCapa < 1e-6:
              ri.inputCapa = abs(charge) / vdd * 1e15

            r = ri.addArc(polarityString + "_" + probe.title).addCapacitance(capa).addInputSlew(slew)
            r.delay = delay * 1e12
            r.transition = transition * 1e12
            r.power = abs(powerCharge) * vdd * 1e15


  def plotResults(self, analysis, *nodes):

    vdd = self._config.nom_voltage

    figure = plt.figure(1, (20, 10))
    plt.title("Waveform")
    plt.xlabel('Time [s]')
    plt.ylabel('Voltage [V]')
    plt.grid()

    legend = []
    for n in nodes:
      plt.plot(analysis.time, analysis.__getattr__(n))
      legend.append(n)
    plt.legend(legend, loc=(.05,.1))
    plt.ylim(-vdd * 0.25, vdd * 1.25)

    plt.tight_layout()
    plt.show()


