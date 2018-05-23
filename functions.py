
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

"""
Several port functions

Port functions are objects that can be assigned to 
ports to designate it's functionality. "High"
and "Low" are static logic states. 

"PositiveTransition" and "NegativeTransition" are 
inputs which are driver with a rising or falling edge 
respectively.

"Probe" is an output.
"""

class Function(object):
  
  """
  Base class for functions that can be assigned to ports
  """

  def makeCircuit(self, circuit, port, vdd, slew, capa, config):
    """
    Creates the circuitry attached to the given port
    """
    pass

  def isInput(self, polarity):
    """
    Returns true, if the function designates an input port with the given polarity
    polarity == True means positive edge, False means negative edge.
    """
    return False

  def isOutput(self):
    """
    Returns true, if the function designates an output port
    """
    return False


class High(Function):

  """
  Designates a port as input driven by a static high signal
  """

  def makeCircuit(self, circuit, port, vdd, slew, capa, config, polarity):
    circuit.VoltageSource("high_" + port, port, "gnd", vdd)


class Low(Function):

  """
  Designates a port as input driven by a static low signal
  """

  def makeCircuit(self, circuit, port, vdd, slew, capa, config, polarity):
    circuit.VoltageSource("low_" + port, port, "gnd", 0)


class PositiveTransition(Function):

  """
  Designates a port as input driven by a rising edge
  """

  def makeCircuit(self, circuit, port, vdd, slew, capa, config, polarity):
    forever = 1@u_s
    circuit.PulseVoltageSource("stim_" + port, port, "gnd", 0, vdd, forever, forever, config.setup@u_ps, slew@u_ps)

  def isInput(self, polarity):
    return polarity == True


class NegativeTransition(Function):

  """
  Designates a port as input driven by a falling edge
  """

  def makeCircuit(self, circuit, port, vdd, slew, capa, config, polarity):
    forever = 1@u_s
    circuit.PulseVoltageSource("stim_" + port, port, "gnd", vdd, 0, forever, forever, config.setup@u_ps, slew@u_ps)

  def isInput(self, polarity):
    return polarity == False


class Edge(Function):

  """
  Designates a port as input driven by a falling edge
  """

  def makeCircuit(self, circuit, port, vdd, slew, capa, config, polarity):
    if polarity:
      t = PositiveTransition()
    else:
      t = NegativeTransition()
    t.makeCircuit(circuit, port, vdd, slew, capa, config, polarity)

  def isInput(self, polarity):
    return True


class Probe(Function):

  """
  Identifies a port as output
  """

  title = ""
  def __init__(self, title):
    self.title = title
    
  def makeCircuit(self, circuit, port, vdd, slew, capa, config, polarity):
    circuit.C("load_" + port, port, "gnd", capa * 1e-15)
    # provide an additional 1M resistor as dummy load for the floating node
    circuit.R("load_" + port, port, "gnd", 1e6)
    
  def isOutput(self):
    return True

