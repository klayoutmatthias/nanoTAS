
# NOTE: for more details see the "buf_x2" and "inv_x1"
# samples.

# specifies the subcircuit pins
# "power" and "gnd" ports are mandatory. The other
# port names are arbitrary, word-like names.
# i0 and i1 are inputs, nq is the output.
pins("i0", "i1", "nq", "power", "gnd")

# First measurement: drive i0 with an edge (positive
# or negative) while keeping i1 high.
i0(edge)
i1(high)
nq(probe("i0_nq"))
collect()

# First measurement: drive i1 with an edge (positive
# or negative) while keeping i0 high.
i0(high)
i1(edge)
nq(probe("i1_nq"))
collect()

