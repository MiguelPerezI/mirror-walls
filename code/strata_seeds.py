"""Activity per boundary stratum, several seeds: mean and standard error per codimension (mirror box).
usage: python3 strata_seeds.py a N2 T2 N3 T3 seeds"""
import sys, numpy as np
from contca import step, codim
DEC, TH = 9, 0.05
a = float(sys.argv[1]); N2, T2, N3, T3, S = map(int, sys.argv[2:7])
def rstep(u):
    return np.round(step(u, a, 1.0/(2*u.ndim+1), 'neumann'), DEC)
def activity(u):
    acts = []
    for m in range(u.ndim):
        for sgn in (-1, 1):
            d = np.mod(u - np.roll(u, sgn, m), 1.0); d = np.minimum(d, 1-d)
            idx = [slice(None)]*u.ndim; idx[m] = 0 if sgn == 1 else -1; d[tuple(idx)] = 0.0
            acts.append(d)
    return np.max(acts, axis=0) > TH
for n, N, T in ((2, N2, T2), (3, N3, T3)):
    shape = (N,)*n; cd = codim(shape); res = []
    grids = np.meshgrid(*[np.arange(N)]*n, indexing='ij')
    dist = np.min([np.minimum(g, N-1-g) for g in grids], axis=0); dres = []
    for seed in range(S):
        rng = np.random.default_rng(100 + seed); u = np.round(rng.random(shape), DEC)
        tot = np.zeros(shape); cnt = 0
        for t in range(T):
            if t >= T//3: tot += activity(u); cnt += 1
            u = rstep(u)
        prof = tot/cnt
        res.append([prof[cd == c].mean() for c in range(n+1)])
        dres.append([prof[dist == k].mean() for k in range(6)])
    res = np.array(res); dres = np.array(dres); se = res.std(axis=0, ddof=1)/np.sqrt(S)
    print(f"n={n} N={N} T={T} a={a} seeds={S}: " + ' '.join(f"codim{c}={res[:,c].mean():.3f}+-{se[c]:.3f}" for c in range(n+1))
          + " | dist0..5: " + ' '.join(f"{x:.3f}" for x in dres.mean(axis=0)), flush=True)
