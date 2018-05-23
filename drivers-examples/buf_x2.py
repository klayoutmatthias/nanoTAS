
# specifies the subcircuit pins
# "power" and "gnd" ports are mandatory. The other
# port names are arbitrary, word-like names.
pins("i", "q", "power", "gnd")

# Specifies the load capacitances in fF
# This line is optional. If missing the capa_table
# from the configuration file is used
capa_table(4,8, 16, 32, 64)

# Specifies the input slews in ps
# This line is optional. If missing the slew_table
# from the configuration file is used
# slew_table(50, 100, 200, 400, 800)

# Declares node "i" as the edge-driven node
# "i" is the name used in the "pins" declaration above
i(edge)

# Declares node "nq" as the output to be probed
# "i_q" is the description string for this measurement
# ("i to q")
q(probe("i_q"))

# Runs the analysis
collect()


