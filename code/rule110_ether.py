"""Rule 110 in a mirror box of 1400 cells: fraction of cells covered by an ether word (the 14-cell word centred on
the cell is one of the words of the ether 11000100110111 over its temporal period 7, eca.defects with the fixed
word set), from random data, every 500 steps up to step 8000. Two runs, the first two seeds of eca_box.py
(default_rng(0) and default_rng(1)); the ring with the same initial data is printed as a control.
usage: python3 rule110_ether.py"""
import numpy as np
from eca import step, defects, ether_words
N, P, T, EVERY, SEEDS = 1400, 14, 8000, 500, (0, 1)
ether_words(110, [1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1], 7)
checks = list(range(0, T + 1, EVERY))
print(f"ether fraction at steps {checks[0]}..{checks[-1]} (every {EVERY})")
for bc in ('mirror', 'periodic'):
    for seed in SEEDS:
        u = np.random.default_rng(seed).integers(0, 2, N); frac = {}
        for t in range(T + 1):
            if t in checks: frac[t] = 1 - defects(u, P, bc, 110).mean()
            u = step(u, 110, bc)
        print(f"{'box' if bc == 'mirror' else 'ring':4s} seed {seed}: " + ' '.join(f"{t}:{frac[t]:.2f}" for t in checks), flush=True)
