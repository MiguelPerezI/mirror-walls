"""Rule 54: one small random patch in an ether-filled mirror box of 401 cells (walls on '1', ether-compatible).
The patch emits a few structures; we count movers before and after they reach the walls."""
import numpy as np
from eca import step, defects, clusters, ether_words, track, velocity
from pngio import write_gray, upscale, montage
ether_words(54, [1,0,0,0], 4)
M = 401; tiles = []
def count_kinds(box, T=160):
    tr, _, _ = track(box.copy(), 54, 'mirror', 4, T=T, t0=0, gap=2)
    mv = sum(1 for x in tr if len(x['t']) >= 80 and abs(velocity(x, M, 'mirror')) > 0.5)
    st = sum(1 for x in tr if len(x['t']) >= 80 and abs(velocity(x, M, 'mirror')) <= 0.5)
    return mv, st
for seed in range(6):
    rng = np.random.default_rng(seed)
    box = np.tile(np.array([1,0,0,0]), M//4 + 1)[:M]; box[196:204] = rng.integers(0, 2, 8)
    rows = []; snap = {}
    for k in range(900):
        if k in (60, 500, 740): snap[k] = count_kinds(box)
        rows.append(defects(box, 4, 'mirror', 54)); box = step(box, 54, 'mirror')
    D = np.array(rows, float)
    wall = D[:, :6].mean(axis=1) + D[:, -6:].mean(axis=1)
    print(f"seed {seed}: (movers, stationary) at t=60: {snap[60]}, t=500: {snap[500]}, t=740: {snap[740]}; "
          f"defect density at walls (6 cells) early {wall[:150].mean():.3f}, late {wall[-150:].mean():.3f}")
    tiles.append(upscale((255*(1-D[::3])).astype(np.uint8), 1))
write_gray('../figures/rule54_single_patch.png', montage(tiles, cols=3, gap=8)); print('ok')
