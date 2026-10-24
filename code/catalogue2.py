import numpy as np
from tracker import run_tracks, velocity, clusters, active, step
a, N = 0.398, 600
rng = np.random.default_rng(0); u = np.round(rng.random(N), 9)
tracks, _ = run_tracks(u, a, 'periodic', T=4000, t0=1000)
sel = [tr for tr in tracks if len(tr['t']) >= 50]
vs = np.array([velocity(tr, N, 'periodic') for tr in sel]); ws = np.array([np.mean(tr['w']) for tr in sel]); ls=np.array([len(tr['t']) for tr in sel])
print(f"tracks with lifetime >= 50: {len(sel)}")
hist, edges = np.histogram(vs, bins=np.arange(-0.55, 0.6, 0.05))
for h, e in zip(hist, edges[:-1]):
    if h: print(f"  v in [{e:+.2f},{e+0.05:+.2f}) : {h:4d}   mean width {ws[(vs>=e)&(vs<e+0.05)].mean():.1f}")
slow = np.abs(vs) < 0.05
print(f"summary: movers (|v| >= 0.05) {(~slow).sum()}, mean |v| {np.abs(vs[~slow]).mean():.3f}, mean width {ws[~slow].mean():.2f}; "
      f"slow (|v| < 0.05) {slow.sum()} = {slow.mean():.3f} of tracks, mean width {ws[slow].mean():.2f}")
# number of clusters alive per step, late
rng = np.random.default_rng(0); u = np.round(rng.random(N), 9)
for t in range(4000):
    if t in (1000, 2000, 3000, 3999): print(f"t={t}: clusters={len(clusters(active(u,'periodic')))}, active fraction={active(u,'periodic').mean():.3f}")
    u = step(u, a, 'periodic')
