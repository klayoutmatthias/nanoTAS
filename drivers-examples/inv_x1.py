
# specifies the subcircuit pins
pins("i", "nq", "power", "gnd")

capa_table(1, 2, 4, 8, 16)

i(edge)
nq(probe("i_nq"))
collect()

