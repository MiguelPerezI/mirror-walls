"""Activity per boundary stratum (by codimension) for the box CA with mirror walls, n = 2 and 3.
usage: python3 strata.py a N2 T2 N3 T3"""
import sys, numpy as np
from contca import step, codim
DEC, TH = 9, 0.05
a = float(sys.argv[1]); N2, T2, N3, T3 = map(int, sys.argv[2:6])
def rstep(u, a):
    n = u.ndim; return np.round(step(u, a, 1.0/(2*n+1), 'neumann'), DEC)
def activity(u):
    # max over all existing neighbour differences (both directions, every axis); mirror duplicates are harmless
    acts = []
    for m in range(u.ndim):
        for sgn in (-1, 1):
            d = np.mod(u - np.roll(u, sgn, m), 1.0); d = np.minimum(d, 1-d)
            idx = [slice(None)]*u.ndim; idx[m] = 0 if sgn == 1 else -1; d[tuple(idx)] = 0.0   # no neighbour there
            acts.append(d)
    return np.max(acts, axis=0) > TH
rng = np.random.default_rng(11)
for n, N, T in ((2, N2, T2), (3, N3, T3)):
    shape = (N,)*n; cd = codim(shape)
    tot = np.zeros(shape); cnt = 0
    u = np.round(rng.random(shape), DEC)
    for t in range(T):
        if t >= T//3: tot += activity(u); cnt += 1
        u = rstep(u, a)
    prof = tot/cnt
    # exclude the last node along each axis from the per-codim means? no: its own activity is measured via other axes
    line = ' '.join(f"codim{c}={prof[cd==c].mean():.3f}(n={int((cd==c).sum())})" for c in range(n+1))
    # distance-to-nearest-wall profile (interior rows only)
    grids = np.meshgrid(*[np.arange(N)]*n, indexing='ij')
    dist = np.min([np.minimum(g, N-1-g) for g in grids], axis=0)
    dprof = ' '.join(f"{prof[dist==k].mean():.3f}" for k in range(6))
    print(f"n={n} N={N} T={T} a={a}: {line} | activity vs distance to nearest wall 0..5: {dprof}")
    if n == 2:
        from pngio import write_gray, upscale
        d = np.mod(u - np.roll(u,-1,1), 1.0); d = np.minimum(d, 1-d)
        write_gray(f'../figures/box2d_a{a}.png', upscale((255*(1-np.minimum(1,4*d))).astype(np.uint8), 2))
