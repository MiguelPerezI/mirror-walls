"""2-D candidates: final frame + space-time cut of the middle row, periodic."""
import numpy as np
from pngio import write_gray, montage
N, T, DEC = 128, 1200, 9
def step(u, a):
    m = (u + np.roll(u,1,0) + np.roll(u,-1,0) + np.roll(u,1,1) + np.roll(u,-1,1))/5.0
    return np.round(np.mod(m + a, 1.0), DEC)
def disp(d): d = np.mod(d, 1.0); d = np.minimum(d, 1-d); return (255*(1-np.minimum(1, 4*d))).astype(np.uint8)
rng = np.random.default_rng(7); tiles = []
for a in (0.33, 0.49, 0.51, 0.67, 0.02, 0.398):
    u = np.round(rng.random((N,N)), DEC); cut = []
    pers = []
    prev = None
    for t in range(T):
        d = np.mod(u - np.roll(u,-1,1), 1.0); d = np.minimum(d, 1-d); A = d > 0.05
        if t >= T - 256: cut.append(d[N//2])
        if prev is not None and t > T//2: pers.append((A & prev).sum()/max(1, A.sum()))
        prev = A; u = step(u, a)
    tiles.append(disp(u - np.roll(u,-1,1))); tiles.append(disp(np.array(cut)))
    print(f"a={a:.3f}  late activity={A.mean():.3f}  persistence P(active at t+1 | active at t)={np.mean(pers):.3f} (random would be {A.mean():.3f})")
write_gray('../figures/cuts2d_frames.png', montage(tiles[0::2], cols=6))
write_gray('../figures/cuts2d_spacetime.png', montage(tiles[1::2], cols=6))
