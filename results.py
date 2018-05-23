
"""
Provides the result objects

The hierarcy is:

  Output -> Input -> Arc -> Capacitances -> InputSlews (delay, transition)

"""

import sys

class Output(object):

  """
  Represents the results for one output port
  """

  name = None
  inputs = None

  def __init__(self, name):
    self.name = name
    self.inputs = []

  def addInput(self, name):
    for o in self.inputs:
      if o.name == name:
        return o
    o = Input(name)
    self.inputs.append(o)
    return o


class Input(object):

  """
  Represents the results for one input port
  """

  name = None
  arcs = None
  inputCapa = 0.0

  def __init__(self, name):
    self.name = name
    self.arcs = []

  def addArc(self, name):
    for o in self.arcs:
      if o.name == name:
        return o
    o = Arc(name)
    self.arcs.append(o)
    return o


class Arc(object):

  """
  Represents the result for one arc (edge to edge)
  """

  name = None
  capas = None

  def __init__(self, name):
    self.name = name
    self.capas = []

  def addCapacitance(self, value):
    for o in self.capas:
      if abs(o.value - value) < 1e-6:
        return o
    o = Capacitance(value)
    self.capas.append(o)
    return o


class Capacitance(object):

  """
  Represents the result for capacitance value in the lookup table
  """

  value = None
  slews = None

  def __init__(self, value):
    self.value = value
    self.slews = []

  def addInputSlew(self, value):
    for o in self.slews:
      if abs(o.value - value) < 1e-6:
        return o
    o = InputSlew(value)
    self.slews.append(o)
    return o


class InputSlew(object):

  """
  Represents the result for capacitance value in the lookup table
  """

  value = None
  delay = 0.0
  transition = 0.0
  power = 0.0

  def __init__(self, value):
    self.value = value


class Results(object):

  """
  Represents the results for one cell
  """

  name = None
  outputs = None

  def __init__(self, name):
    self.outputs = []
    self.name = name

  def addOutput(self, name):
    for o in self.outputs:
      if o.name == name:
        return o
    o = Output(name)
    self.outputs.append(o)
    return o

  def write(self, file = sys.stdout):

    for output in self.outputs:

      file.write("pin(" + output.name + "):\n")

      for input in output.inputs:

        file.write("  related_pin(" + input.name + "):\n")
        file.write("    cap: %.2f fF\n" % input.inputCapa)

        for arc in input.arcs:

          file.write("    arc(" + arc.name + "):\n")

          slewLine = ", ".join([ "%-8.2f" % s.value for s in arc.capas[0].slews ])

          for prop in [ "delay", "transition", "power" ]:

            file.write("      " + prop + ":\n")
            file.write("        # " + slewLine + "     # input slew (ps)\n")

            for capa in arc.capas:
              line = ", ".join([ "%-8.2f" % s.__dict__[prop] for s in capa.slews ])
              file.write("        [ " + line + " ]   # C=" + ("%.2f" % capa.value) + "fF\n")


