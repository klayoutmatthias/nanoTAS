
import sys
import os

# lookup "config.py" from the current path
sys.path.append(".")

import config

import glob
from driver import *

for fn in glob.glob(config.drivers):

  name = os.path.splitext(os.path.basename(fn))[0]
  print("----------------------------------------------------------------------------------")
  print("\nRunning nanoTAS on cell " + name + " ...\n")

  with open(fn) as file:
    driver = Driver(name, config)
    exec(file.read(), globals(), driver.vars)
    driver.results.write()

