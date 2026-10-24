"""Rule 54, exhaustive and detector-free.
The ether (tile 1000, period 4) is known exactly, so a structure is a cluster of cells where the state differs
from the ether at the same time. (1) Insert every binary word of length L into the ether and keep the ones that
leave exactly one right mover: this gives every phase class of the isolated right mover w+.
(2) Wall: each class meets the mirror wall of a box of length 4k+1 in a fixed number of ways; record the outcome.
(3) Torus: every head-on collision of a w+ class with a w- class (mirror images), all relative offsets; the
movers before the collision are counted, so a single mover against a train is reported as such.
Writes rule54_examples.npy (the train event and the single-mover event) for fig_rule54.py.
usage: python3 rule54_exact.py [L]"""
import sys, numpy as np
from collections import Counter
from eca import step
TILE = np.array([1, 0, 0, 0])
def ether(N): return np.tile(TILE, N//4 + 1)[:N]
def evolve(u, bc, T):
    E = ether(len(u)); rows = []
    for _ in range(T):
        rows.append(u != E); u = step(u, 54, bc); E = step(E, 54, bc)
    return u, E, np.array(rows)
def blobs(diff, gap=2):
    idx = np.flatnonzero(diff); out = []
    if idx.size == 0: return out
    s = p = idx[0]
    for i in idx[1:]:
        if i - p > gap + 1: out.append((s + p)/2); s = i
        p = i
    out.append((s + p)/2); return out
def census(u, bc, T=40):
    """structures after the system has settled: count blobs and their velocities over T steps (no wrap issues:
    used only when structures are far from the torus seam and from each other)"""
    _, _, R = evolve(u.copy(), bc, T + 1)
    b0, b1 = blobs(R[0]), blobs(R[T])
    if len(b0) != len(b1): return None
    out = Counter()
    for x0, x1 in zip(sorted(b0), sorted(b1)):
        v = (x1 - x0)/T; out['w+' if v > 0.5 else 'w-' if v < -0.5 else 'g'] += 1
    return dict(out)
L = int(sys.argv[1]) if len(sys.argv) > 1 else 10
N = 400; classes = {}
for code in range(1, 2**L):
    word = np.array([(code >> k) & 1 for k in range(L)])
    for off in range(4):
        u = ether(N); u[100+off:100+off+L] = word
        if np.array_equal(u, ether(N)): continue
        u, E, R = evolve(u, 'periodic', 160)            # 160 = 0 mod 4
        if census(u, 'periodic') != {'w+': 1}: continue
        d = np.flatnonzero(u != E)
        key = (d[0] % 4, (u[d[0]:d[0]+12] != E[d[0]:d[0]+12]).tobytes())   # residue + shape at t = 0 mod 4
        classes.setdefault(key, (word.copy(), off))
def train_sizes(u, E, gap=2):
    """movers per blob at t = 0 mod 4, in position order: a train of k movers four cells apart has 2k off-ether cells"""
    idx = np.flatnonzero(u != E)
    return [len(g)//2 for g in np.split(idx, np.flatnonzero(np.diff(idx) > gap + 1) + 1)] if idx.size else []
def train_name(k): return "single mover" if k == 1 else f"train of {k} movers"
def class_size(cls):
    word, off = cls; u = ether(400); u[100+off:100+off+L] = word
    u, E, _ = evolve(u, 'periodic', 160); return train_sizes(u, E)[0]
print(f"L={L}: phase classes of an isolated right mover (residue mod 4 at t = 0 mod 4, shape): {len(classes)}")
for k, cls in classes.items(): print("   residue", k[0], "shape", np.frombuffer(k[1], dtype=bool).astype(int), f"({train_name(class_size(cls))})")
def make_wplus(N, pos, cls):
    """ether of length N with the class-cls right mover generated at pos (multiple of 4), state at t = 160"""
    word, off = cls; u = ether(N); u[pos+off:pos+off+L] = word
    u, E, _ = evolve(u, 'periodic' if N % 4 == 0 else 'mirror', 160); return u
# (2) wall events: right mover approaching the right wall of a mirror box; start offset s = 0..7 covers all phases
M = 4*120 + 1; wall = Counter()
for ci, cls in enumerate(classes.values()):
    for s in range(8):
        word, off = cls; u = ether(M); p = 4*60 + s
        # generate in the bulk with mirror evolution (wall far away for the first 160 steps)
        u[p+off:p+off+L] = word
        u, E, _ = evolve(u, 'mirror', 160)
        if census(u, 'mirror') != {'w+': 1}: continue
        u2, E2, _ = evolve(u, 'mirror', 400)
        c = census(u2, 'mirror'); left = int((u2 != E2).sum())
        wall[(ci, s % 4, str(c), left)] += 1
print("wall events (class, start residue, census after, cells off-ether after) -> count")
for k, n in sorted(wall.items()): print("   ", k, n, f"  [class {k[0]} = {train_name(class_size(list(classes.values())[k[0]]))}]")
# (3) torus head-on: seeds of the single right-mover class and of the single left-mover class, all offsets
def harvest(kind):
    out = {}
    for code in range(1, 2**L):
        word = np.array([(code >> k) & 1 for k in range(L)])
        for off in range(4):
            u = ether(400); u[100+off:100+off+L] = word
            if np.array_equal(u, ether(400)): continue
            u, E, _ = evolve(u, 'periodic', 160)
            if census(u, 'periodic') != {kind: 1}: continue
            d = np.flatnonzero(u != E)
            if d[-1] - d[0] > 3: continue                # single mover, not a train
            out.setdefault(d[0] % 4, (word.copy(), off))
    return out
R_, L_ = harvest('w+'), harvest('w-')
print(f"single-mover classes: right {[int(r) for r in sorted(R_)]}, left {[int(r) for r in sorted(L_)]} (residue of first off-ether cell at t = 0 mod 4)")
# The single left-mover seed placed at offset q gives a single left mover only for q = 0 mod 4; at other offsets
# it generates a train (one blob, so the blob census below still reads {'w+': 1, 'w-': 1}). The train sizes
# before the collision are therefore recorded separately, from the off-ether cells at t = 32.
N = 480; heads = Counter(); examples = {}; kinds = Counter(); qres = {}; ex2 = {}
for ri, (w0, o0) in R_.items():
    for li, (w1, o1) in L_.items():
        for q in range(16):
            u = ether(N); u[100+o0:100+o0+L] = w0; u[300+q+o1:300+q+o1+L] = w1
            pre, Epre, _ = evolve(u.copy(), 'periodic', 32)
            if census(pre, 'periodic') != {'w+': 1, 'w-': 1}: continue
            post, E, _ = evolve(u.copy(), 'periodic', 400)
            c = census(post, 'periodic'); key = (str(c), int((post != E).sum()))
            heads[key] += 1; examples.setdefault(key, (q, u.copy()))
            kp, km = train_sizes(pre, Epre)                 # w+ seed sits left of the w- seed
            k2 = (f"{train_name(kp)} (w+) vs {train_name(km)} (w-)",) + key
            kinds[k2] += 1; qres.setdefault(k2, set()).add(q % 4); ex2.setdefault(k2, u.copy())
print("torus head-on collisions, one w+ blob against one w- blob (census after 400 steps, cells off-ether) -> number of offsets q")
for k, n in sorted(heads.items()): print("   ", k, n)
print("the same, split by the movers before the collision (t = 32):")
for k, n in sorted(kinds.items()): print("   ", k, n, f"offsets, q mod 4 in {sorted(qres[k])}")
single = sorted({k[1:] for k in kinds if k[0].startswith("single mover (w+) vs single mover")})
print(f"head-on collisions of two single movers: {len(single)} outcome class(es): "
      + ', '.join('annihilation, pure ether left' if k == ('{}', 0) else str(k) for k in single))
def mirror_nodes(u):
    """nodes c of the ring about which the state is mirror-symmetric, u[c+k] = u[c-k] for all k"""
    i = np.arange(len(u)); return [c for c in range(len(u)) if np.array_equal(u, u[(2*c - i) % len(u)])]
for k2, u0 in sorted(ex2.items()):
    if not k2[0].startswith("single mover (w+) vs single mover"): continue
    u, _, _ = evolve(u0.copy(), 'periodic', 32); cs = mirror_nodes(u); sym = bool(cs)
    for t in range(32, 400):
        sym &= all(np.array_equal(u, u[(2*c - np.arange(N)) % N]) for c in cs); u = step(u, 54, 'periodic')
    print(f"  {k2[0]}: state mirror-symmetric about the nodes {cs} at every step t = 32..400: {sym}")
np.save('rule54_examples.npy', np.array([examples[k][1] for k in sorted(examples)]))
print("example offsets:", {k: examples[k][0] for k in sorted(examples)})
