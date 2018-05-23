
# specifies the subcircuit pins
# "power" and "gnd" ports are mandatory. The other
# port names are arbitrary, word-like names.
pins("i", "nq", "power", "gnd")

# Specifies the load capacitances in fF
# This line is optional. If missing the capa_table
# from the configuration file is used
capa_table(1, 2, 4, 8, 16)

# Specifies the input slews in ps
# This line is optional. If missing the slew_table
# from the configuration file is used
slew_table(50, 100, 200, 400, 800)

# declares node "i" as the edge-driven node
# "i" is the name used in the "pins" declaration above
i(edge)

# declares node "nq" as the output to be probed
# "i_nq" is the description string for this measurement
# ("i to nq")
nq(probe("i_nq"))

# runs the analysis
collect()

