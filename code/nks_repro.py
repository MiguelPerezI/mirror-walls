"""Reproduce NKS p.244 class-4 continuous CAs: u' = frac((kL*u_{i-1} + u_i + kR*u_{i+1})/3 + a),
with fixed-precision rounding (emulating exact arithmetic), random ICs, periodic; show difference display."""
import numpy as np
from pngio import write_gray, montage
N, T, DEC = 400, 800, 9
def step(u, a, k, bc):
    if bc == 'periodic':
        L, R = np.roll(u, 1), np.roll(u, -1)
    else:  # neumann mirror ghosts
        L, R = np.roll(u, 1), np.roll(u, -1); L[0] = u[1]; R[-1] = u[-2]
    return np.round(np.mod((k*L + u + k*R)/3.0 + a, 1.0), DEC)
def run(a, k, bc, seed=3):
    rng = np.random.default_rng(seed); u = rng.random(N); u = np.round(u, DEC)
    st = np.zeros((T, N)); act = np.zeros(T)
    for t in range(T):
        st[t] = u
        d = np.abs(np.roll(u,-1) - u); act[t] = (d > 1e-6).mean()
        u = step(u, a, k, bc)
    return st, act
tiles = []
for a, k in ((0.398, 1.0), (0.4, 1.0), (0.5, 1.13), (0.3, 1.0)):
    for bc in ('periodic', 'neumann'):
        st, act = run(a, k, bc)
        diff = np.mod(st - np.roll(st, -1, axis=1), 1.0)   # Wolfram's difference display
        diff[:, -1] = 0 if bc == 'neumann' else diff[:, -1]
        tiles.append((255*(1-np.minimum(1, 4*diff[::2]))).astype(np.uint8))  # 400 rows x 400 cols
        A = act[T//2:]
        print(f"a={a:5.3f} k={k:4.2f} {bc:8s}  active fraction (late) mean={A.mean():.3f} min={A.min():.3f} max={A.max():.3f}")
write_gray('../figures/nks_repro.png', montage(tiles, cols=2))
