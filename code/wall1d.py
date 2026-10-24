"""1-D class-4 candidate a=0.398: periodic vs Neumann (mirror) walls.
Activity = symmetric neighbour difference mod 1 exceeding 0.05. Profile vs distance to wall."""
import numpy as np
from pngio import write_gray, montage, upscale
N, T, DEC, TH = 400, 3000, 9, 0.05
def step(u, a, k, bc):
    L, R = np.roll(u, 1), np.roll(u, -1)
    if bc == 'neumann': L[0] = u[1]; R[-1] = u[-2]
    return np.round(np.mod((k*L + u + k*R)/3.0 + a, 1.0), DEC)
def symdiff(u, bc):
    d = np.mod(u - np.roll(u, -1), 1.0); d = np.minimum(d, 1-d)
    if bc == 'neumann': d[-1] = 0.0
    return d
a, k = 0.398, 1.0
for bc in ('periodic', 'neumann'):
    prof = np.zeros(N); cnt = 0; tiles = []
    for seed in range(4):
        rng = np.random.default_rng(seed); u = np.round(rng.random(N), DEC)
        st = []
        for t in range(T):
            d = symdiff(u, bc)
            if t >= 500: prof += (d > TH); cnt += 1
            if seed == 0 and t % 3 == 0: st.append(d)
            u = step(u, a, k, bc)
        if seed == 0:
            S = np.array(st)  # 1000 x 400
            img = (255*(1-np.minimum(1, 2*S))).astype(np.uint8)
            write_gray(f'../figures/wall1d_{bc}_full.png', img)
            write_gray(f'../figures/wall1d_{bc}_leftwall.png', upscale(img[:, :60], 3))
    prof /= cnt
    bulk = prof[100:300].mean()
    print(f"{bc:8s}  bulk activity={bulk:.3f}   first 12 cells: {np.round(prof[:12],3)}   last 12: {np.round(prof[-12:],3)}")
    print(f"          mean activity in 10 cells nearest walls / bulk = {np.concatenate([prof[:10],prof[-10:]]).mean()/bulk:.2f}")
