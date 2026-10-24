"""
CuPy version of contca.py: rule (1), u' = frac(u + sum_m r d2_m u + a), with ternary-cube mirror
ghosts ('neumann': u_{-1}=u_1, u_N=u_{N-2}) or wrap ('periodic'), n = 2 or 3, one fused kernel per
step. Axes before the last n are batch axes (many seeds in one call).
Same operation order as contca.py / strata_seeds.py and numpy's rounding rint(x*10^dec)/10^dec,
with round-to-nearest intrinsics (no fma), so states are bit-identical to the CPU scripts.
usage (self-test): python contca_gpu.py
"""
import cupy as cp, numpy as np

_PRE = r'''
#define ADD(x,y) __dadd_rn(x,y)
#define SUB(x,y) __dsub_rn(x,y)
#define MUL(x,y) __dmul_rn(x,y)
#define DIV(x,y) __ddiv_rn(x,y)
__device__ double mod1(double x){            // numpy mod(x, 1.0)
    double m = fmod(x, 1.0);
    if (m != 0.0) { if (m < 0.0) m = ADD(m, 1.0); } else m = 0.0;
    return m; }
__device__ int nb(int i, int d, int N, int per){   // neighbour index: wrap or mirror ghost
    int j = i + d;
    if (j < 0)  return per ? N-1 : 1;
    if (j >= N) return per ? 0 : N-2;
    return j; }
'''

def _index(n):   # flat index i -> batch base, spatial indices i0.., strides s0.., centre c
    s = ["long t = i;"]
    for m in reversed(range(n)):
        s.append(f"int i{m} = t % N{m}; t /= N{m};")
    s.append("long base = t" + ''.join(f"*N{m}" for m in range(n)) + ";")
    for m in range(n):
        s.append(f"long s{m} = 1" + ''.join(f"*N{k}" for k in range(m+1, n)) + ";")
    s.append("long c = base" + ''.join(f" + i{m}*s{m}" for m in range(n)) + ";")
    return '\n'.join(s)

def _args(n):
    return ', '.join(f"int32 N{m}" for m in range(n))

_cache = {}
def _step_kernel(n):
    if ('step', n) not in _cache:
        body = _index(n) + "\ndouble uc = u[c], lap = 0.0, up, dn;\n"
        for m in range(n):
            body += (f"up = u[c + (nb(i{m}, 1, N{m}, per) - i{m})*s{m}];\n"
                     f"dn = u[c + (nb(i{m}, -1, N{m}, per) - i{m})*s{m}];\n"
                     f"lap = ADD(lap, MUL(r, ADD(SUB(up, MUL(2.0, uc)), dn)));\n")
        body += "double w = mod1(ADD(ADD(uc, lap), a));\nv = f > 0 ? DIV(rint(MUL(w, f)), f) : w;"
        _cache[('step', n)] = cp.ElementwiseKernel(
            f'raw float64 u, float64 a, float64 r, float64 f, int32 per, {_args(n)}',
            'float64 v', body, f'contca_step{n}', preamble=_PRE)
    return _cache[('step', n)]

def _act_kernel(n):
    if ('act', n) not in _cache:
        body = _index(n) + "\ndouble uc = u[c], x; int act = 0;\n"
        for m in range(n):
            for d in (-1, 1):
                body += (f"if (per || (i{m}+({d}) >= 0 && i{m}+({d}) < N{m})) {{\n"
                         f"  x = mod1(SUB(uc, u[c + (nb(i{m}, {d}, N{m}, per) - i{m})*s{m}]));\n"
                         f"  x = fmin(x, SUB(1.0, x)); if (x > th) act = 1; }}\n")
        body += "out = act;"
        _cache[('act', n)] = cp.ElementwiseKernel(
            f'raw float64 u, float64 th, int32 per, {_args(n)}',
            'float64 out', body, f'contca_act{n}', preamble=_PRE)
    return _cache[('act', n)]

def step(u, a, r, bc, dec=None, n=None, out=None):
    """one step of rule (1); dec = decimals to round to (as np.round), None = no rounding"""
    n = n or u.ndim
    f = 10.0**dec if dec is not None else 0.0
    if out is None: out = cp.empty_like(u)
    return _step_kernel(n)(u, a, r, f, int(bc == 'periodic'), *map(int, u.shape[-n:]), out)

def rstep(u, a, dec=9, bc='neumann', n=None, out=None):
    n = n or u.ndim
    return step(u, a, 1.0/(2*n+1), bc, dec, n, out)

def activity(u, th=0.05, bc='neumann', n=None, out=None):
    """1.0 where some existing neighbour differs by more than th (distance to Z), as strata_seeds.py"""
    n = n or u.ndim
    if out is None: out = cp.empty_like(u)
    return _act_kernel(n)(u, th, int(bc == 'periodic'), *map(int, u.shape[-n:]), out)

def initial(shape, seed, dec=9):
    """same initial data as strata_seeds.py (seed = 100 + k there)"""
    return np.round(np.random.default_rng(seed).random(shape), dec)

if __name__ == '__main__':
    from contca import step as cstep
    a, dec = 0.398, 9
    def cpu_act(u, th=0.05):
        acts = []
        for m in range(u.ndim):
            for sgn in (-1, 1):
                d = np.mod(u - np.roll(u, sgn, m), 1.0); d = np.minimum(d, 1-d)
                idx = [slice(None)]*u.ndim; idx[m] = 0 if sgn == 1 else -1; d[tuple(idx)] = 0.0
                acts.append(d)
        return np.max(acts, axis=0) > th
    for shape, T, bc in (((64, 64), 200, 'neumann'), ((64, 64), 200, 'periodic'), ((16, 16, 16), 200, 'neumann'), ((16, 16, 16), 200, 'periodic')):
        n = len(shape); r = 1.0/(2*n+1)
        u = initial(shape, 100); g = cp.asarray(u)
        md = 0.0; ma = 0
        for t in range(T):
            u = np.round(cstep(u, a, r, bc), dec)
            g = step(g, a, r, bc, dec)
            md = max(md, np.abs(cp.asnumpy(g) - u).max())
            if bc == 'neumann': ma = max(ma, int((cp.asnumpy(activity(g)) != cpu_act(u)).sum()))
        print(f"{shape} {bc} a={a} T={T}: max|gpu-cpu| over all steps = {md:.3e}, activity mismatches = {ma}, equal arrays = {np.array_equal(cp.asnumpy(g), u)}")
    # batched: 4 seeds in one array equal 4 separate runs
    g = cp.asarray(np.stack([initial((64, 64), 100+s) for s in range(4)]))
    for t in range(50): g = rstep(g, a, n=2)
    ok = True
    for s in range(4):
        h = cp.asarray(initial((64, 64), 100+s))
        for t in range(50): h = rstep(h, a)
        ok &= bool((g[s] == h).all())
    print(f"batched 4 seeds == separate runs: {ok}")
