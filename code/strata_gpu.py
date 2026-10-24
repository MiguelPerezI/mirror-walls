"""Activity per boundary stratum on the GPU, all seeds in one batch: mean and standard error per
codimension (mirror box) and against the distance to the nearest wall. Same measurement, seeds and
rounding as strata_seeds.py (bit-identical states, see contca_gpu.py).
usage: python strata_gpu.py a N2 T2 N3 T3 seeds [K=8]     (K = distances 0..K-1 in the profile)"""
import sys, time, numpy as np, cupy as cp
from contca import codim
from contca_gpu import rstep, activity, initial
DEC, TH = 9, 0.05
a = float(sys.argv[1]); N2, T2, N3, T3, S = map(int, sys.argv[2:7]); K = int(sys.argv[7]) if len(sys.argv) > 7 else 8
def mse(x):   # mean and standard error over seeds (axis 0)
    return x.mean(axis=0), x.std(axis=0, ddof=1)/np.sqrt(len(x)) if len(x) > 1 else 0*x[0]
for n, N, T in ((2, N2, T2), (3, N3, T3)):
    if N == 0: continue
    shape = (N,)*n; cd = cp.asarray(codim(shape).ravel())
    grids = np.meshgrid(*[np.arange(N)]*n, indexing='ij')
    dist = cp.asarray(np.minimum(np.min([np.minimum(g, N-1-g) for g in grids], axis=0), K).ravel())
    u = cp.asarray(np.stack([initial(shape, 100 + seed, DEC) for seed in range(S)]))
    v, tot, act = cp.empty_like(u), cp.zeros_like(u), cp.empty_like(u); cnt = 0
    cp.cuda.Device().synchronize(); t0 = time.time()
    for t in range(T):
        if t >= T//3: tot += activity(u, TH, out=act, n=n); cnt += 1
        rstep(u, a, DEC, out=v, n=n); u, v = v, u
    cp.cuda.Device().synchronize(); dt = time.time() - t0
    prof = (tot/cnt).reshape(S, -1)
    res = np.array([cp.asnumpy(cp.bincount(cd, weights=p)/cp.bincount(cd)) for p in prof])
    dres = np.array([cp.asnumpy(cp.bincount(dist, weights=p)[:K]/cp.bincount(dist)[:K]) for p in prof])
    (m, se), (dm, dse) = mse(res), mse(dres)
    print(f"n={n} N={N} T={T} a={a} seeds={S}: " + ' '.join(f"codim{c}={m[c]:.3f}+-{se[c]:.3f}" for c in range(n+1))
          + f" | dist0..{K-1}: " + ' '.join(f"{x:.3f}+-{e:.3f}" for x, e in zip(dm, dse))
          + f" | gpu {dt:.1f}s for {S} seeds ({dt/S:.2f}s/seed)", flush=True)
    del u, v, tot, act, prof; cp.get_default_memory_pool().free_all_blocks()
