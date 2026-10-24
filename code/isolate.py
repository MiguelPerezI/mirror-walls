"""Isolate one long-lived structure from a torus run, place it alone in a mirror box, and watch it hit the wall."""
import numpy as np
from tracker import run_tracks, velocity, step, active, clusters
from pngio import write_gray, upscale
a, N = 0.398, 600
rng = np.random.default_rng(0); u0 = np.round(rng.random(N), 9)
tracks, _ = run_tracks(u0, a, 'periodic', T=3000, t0=1000)
long = sorted([tr for tr in tracks if len(tr['t']) >= 150], key=lambda tr: -len(tr['t']))
results = []
for k, tr in enumerate(long[:40]):
    t_mid = tr['t'][len(tr['t'])//2]; c = int(round(tr['c'][len(tr['t'])//2])); v = velocity(tr, N, 'periodic')
    # regenerate the state at t_mid
    u = u0.copy()
    for t in range(t_mid): u = step(u, a, 'periodic')
    A = active(u, 'periodic')
    # require the nearest other cluster to be at least 16 cells away
    cl = clusters(A); dists = [abs(0.5*(x[0]+x[1]) - c) for x in cl if abs(0.5*(x[0]+x[1]) - c) > 2]
    lo, hi = c-10, c+10
    if (dists and min(dists) < 16) or lo < 0 or hi >= N: continue
    # background value: a quiet cell far away
    quiet = np.flatnonzero(~A & ~np.roll(A,1) & ~np.roll(A,-1) & ~np.roll(A,2) & ~np.roll(A,-2))
    ub = u[quiet[len(quiet)//2]]
    M = 160; box = np.full(M, ub); start = 40 if v > 0 else 120   # launch towards the nearer wall
    box[start-10:start+11] = u[lo:hi+1]
    rows = []; alive = []
    for t in range(1400):
        Ab = active(box, 'mirror'); rows.append(Ab.astype(float)); alive.append(len(clusters(Ab)))
        box = step(box, a, 'mirror')
    alive = np.array(alive)
    # expected wall hit time: distance / |v|
    dist = (M-1-start) if v > 0 else start; t_hit = int(dist/abs(v)) if abs(v) > 1e-3 else -1
    after = alive[min(len(alive)-1, t_hit+150):].mean() if t_hit > 0 else alive[-200:].mean()
    results.append((k, v, t_hit, alive[:50].mean(), after))
    img = (255*(1-np.array(rows))).astype(np.uint8)
    write_gray(f'../figures/isolate_{k}.png', upscale(img[::2], 2))
    print(f"structure {k}: v={v:+.3f}  launched at {start}, expected wall hit ~t={t_hit}; clusters alive early={alive[:50].mean():.2f}, 150+ steps after hit={after:.2f}; "
          f"clusters at t=200,600,1000,1399: {alive[200]},{alive[600]},{alive[1000]},{alive[1399]}")
