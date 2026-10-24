import numpy as np, sys
from pngio import write_gray, montage
from contca import step, active
N, T = 256, 384
rng = np.random.default_rng(1)
avals = np.round(np.arange(0.0, 1.0, 0.025), 3)
rows = []
print(f"{'a':>6} {'act(rand)':>10} {'act(1cell)':>11} {'ncomp(1cell)':>13} {'width':>6}")
tiles_r, tiles_s = [], []
for a in avals:
    for mode in ('rand', 'single'):
        u = rng.random(N) if mode == 'rand' else np.zeros(N)
        if mode == 'single': u[N//2] = 0.5
        st = np.zeros((T, N))
        acts = []
        for t in range(T):
            st[t] = u
            if t >= T//2: acts.append(active(u, 'periodic').mean())
            u = step(u, a, 1/3, 'periodic')
        act = np.mean(acts)
        img = (255*(1-st)).astype(np.uint8)
        (tiles_r if mode=='rand' else tiles_s).append(img)
        if mode == 'rand': ar = act
        else:
            am = act
            A = active(st[-1], 'periodic')
            # number of active components and total width
            d = np.diff(np.concatenate([[0], A.astype(int), [0]]))
            ncomp = int((d == 1).sum()); width = int(A.sum())
    print(f"{a:6.3f} {ar:10.3f} {am:11.3f} {ncomp:13d} {width:6d}")
write_gray('../figures/scan1d_random.png', montage(tiles_r))
write_gray('../figures/scan1d_single.png', montage(tiles_s))
