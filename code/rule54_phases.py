"""Rule 54: phase classes of every mover seen in random launches (not only isolated ones).
At t = 0 mod 4 the ether is the tile 1000; a mover is a blob of cells off the ether that moves at speed 1.
Record (direction, residue of its first off-ether cell mod 4, its off-ether shape) for every mover that is
isolated (no other off-ether cell within 12 cells) at two consecutive check times."""
import numpy as np
from collections import Counter
from eca import step
TILE = np.array([1, 0, 0, 0]); N = 1200
def ether(N): return np.tile(TILE, N//4 + 1)[:N]
seen = Counter(); gutters = Counter()
for seed in range(1500):
    rng = np.random.default_rng(seed); u = ether(N); w = 20; u[600:600+w] = rng.integers(0, 2, w); E = ether(N)
    prev = None
    for t in range(1, 401):
        u = step(u, 54, 'periodic'); E = step(E, 54, 'periodic')
        if t % 4 or t < 40: continue
        d = np.flatnonzero(u != E)
        if d.size == 0: break
        # isolated blobs
        groups = np.split(d, np.flatnonzero(np.diff(d) > 12) + 1)
        cur = [(g[0], g[-1], (u[g[0]:g[-1]+1] != E[g[0]:g[-1]+1]).astype(int).tobytes()) for g in groups]
        if prev is not None:
            for s, e, sh in cur:
                for s0, e0, sh0 in prev:
                    if sh == sh0 and (s - s0) in (4, -4, 0):
                        kind = {4: 'w+', -4: 'w-', 0: 'g'}[s - s0]
                        (gutters if kind == 'g' else seen)[(kind, int(s % 4), sh.hex() if kind == 'g' else len(sh))] += 1
        prev = cur
print("movers (direction, residue mod 4, extent) -> observations")
for k, n in sorted(seen.items(), key=lambda x: -x[1])[:20]: print("   ", k, n)
print("stationary (kind, residue, shape) -> observations:", len(gutters), "distinct;", sum(gutters.values()), "observations")
for k, n in sorted(gutters.items(), key=lambda x: -x[1])[:6]: print("   ", k, n)
res = {d: sorted({k[1] for k in seen if k[0] == d}) for d in ('w+', 'w-')}
print(f"summary: {sum(seen.values())} mover observations in 1500 launches; residues mod 4 seen: w+ {res['w+']}, w- {res['w-']}")
