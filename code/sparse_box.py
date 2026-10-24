"""Sparse launch: uniform background + one random patch in a mirror box. Structures emerge, travel, hit walls.
Cluster count vs time tells whether reflections conserve structures. Same patch on a torus for comparison."""
import numpy as np
from tracker import step, active, clusters
from pngio import write_gray, upscale
a, M, T = 0.398, 200, 3000
rng = np.random.default_rng(4)
patch = np.round(rng.random(12), 9)
for bc in ('mirror', 'periodic'):
    u = np.full(M, 0.3); u[94:106] = patch; rows = []; cnt = []
    for t in range(T):
        A = active(u, bc); cnt.append(len(clusters(A))); rows.append(A)
        u = step(u, a, bc)
    cnt = np.array(cnt)
    print(f"{bc:8s}: clusters at t=100,300,600,1000,1500,2000,2500,2999 -> " + ','.join(str(cnt[t]) for t in (100,300,600,1000,1500,2000,2500,2999))
          + f"   mean over last 1000 = {cnt[-1000:].mean():.2f}")
    write_gray(f'../figures/sparse_{bc}.png', upscale((255*(1-np.array(rows[::3], float))).astype(np.uint8), 2))
