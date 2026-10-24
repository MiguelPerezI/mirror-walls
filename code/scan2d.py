"""2-D scan of u' = frac(mean5(u) + a) (periodic, random IC): late activity fraction per a."""
import numpy as np
from pngio import write_gray, montage
N, T, DEC, TH = 128, 600, 9, 0.05
def step(u, a):
    m = (u + np.roll(u,1,0) + np.roll(u,-1,0) + np.roll(u,1,1) + np.roll(u,-1,1))/5.0
    return np.round(np.mod(m + a, 1.0), DEC)
def act(u):
    d1 = np.mod(u - np.roll(u,-1,0), 1.0); d1 = np.minimum(d1, 1-d1)
    d2 = np.mod(u - np.roll(u,-1,1), 1.0); d2 = np.minimum(d2, 1-d2)
    return (np.maximum(d1, d2) > TH).mean()
rng = np.random.default_rng(5)
avals = list(np.round(np.arange(0.0, 1.0, 0.01), 3)) + [0.398]
res = []; tiles = []
for a in avals:
    u = np.round(rng.random((N,N)), DEC); acts = []
    for t in range(T):
        if t >= T//2: acts.append(act(u))
        u = step(u, a)
    A = np.array(acts); res.append((a, A.mean(), A.std()))
    if 0.02 < A.mean() < 0.7:
        d = np.mod(u - np.roll(u,-1,1), 1.0); d = np.minimum(d, 1-d)
        tiles.append((255*(1-np.minimum(1, 4*d))).astype(np.uint8))
        print(f"candidate a={a:.3f}  late activity {A.mean():.3f} +- {A.std():.3f}")
print("all:", ' '.join(f"{a:.2f}:{m:.2f}" for a, m, s in res))
if tiles: write_gray('../figures/scan2d_candidates.png', montage(tiles, cols=6))
