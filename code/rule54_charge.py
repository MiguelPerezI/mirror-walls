"""Rule 54, dense runs: right and left mover counts N+, N- over time on the torus and in the mirror box.
A right-mover unit is a pair of adjacent off-ether cells starting at residue 2 (mod 4) at t = 0 mod 4 that reappears
4 cells to the right 4 steps later; left movers likewise at residue 1, 4 cells to the left."""
import sys, numpy as np
from eca import step
TILE = np.array([1, 0, 0, 0])
def ether(N): return np.tile(TILE, N//4 + 1)[:N]
def units(off, res):
    x = np.flatnonzero(off[:-1] & off[1:]); return set(x[x % 4 == res].tolist())
def counts(u, E, bc):
    off0 = u != E; u4, E4 = u, E
    for _ in range(4): u4 = step(u4, 54, bc); E4 = step(E4, 54, bc)
    off4 = u4 != E4; N = len(u)
    a, b = units(off0, 2), units(off4, 2); c, d = units(off0, 1), units(off4, 1)
    sh = (lambda x, s: (x + s) % N) if bc == 'periodic' else (lambda x, s: x + s)
    np_ = sum(1 for x in a if sh(x, 4) in b and x not in d); nm = sum(1 for x in c if sh(x, -4) in d)
    return np_, nm, int(off0.sum())
if __name__ == "__main__":
  T = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
  for bc, N in (('periodic', 1200), ('mirror', 1201)):
      movers = []
      for seed in range(3):
          rng = np.random.default_rng(seed); u = ether(N); u[200:N-200] = rng.integers(0, 2, N-400); E = ether(N)
          out = []
          for t in range(T + 1):
              if t % 1000 == 0 and t > 0: out.append(counts(u, E, bc))
              u = step(u, 54, bc); E = step(E, 54, bc)
          print(bc, seed, "  (N+, N-, off-ether cells) at t=1000..:", out, flush=True)
          movers += [p + m for p, m, _ in out]
      mv = np.array(movers)
      print(f"{bc}: movers N+ + N- over 3 seeds x {len(out)} times: mean {mv.mean():.1f} +- {mv.std(ddof=1)/np.sqrt(len(mv)):.1f} (standard error)", flush=True)
  