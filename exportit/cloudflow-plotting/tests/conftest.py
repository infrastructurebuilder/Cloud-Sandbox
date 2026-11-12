import os

# The plotting modules open a matplotlib figure machinery when they are
# imported; tests have no display.
os.environ.setdefault("MPLBACKEND", "Agg")
