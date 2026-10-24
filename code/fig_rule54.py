"""Figures for rule 54: off-ether display (black where the state differs from the exact ether).
(a) the three elementary events: single head-on collision on the torus, a mover meeting the mirror wall,
    a single mover against a train of four; (b) one sparse launch on the torus and in the mirror box."""
import numpy as np
from eca import step
from pngio import write_gray, montage
from png2pdf import write_pdf
TILE = np.array([1, 0, 0, 0])
def ether(N): return np.tile(TILE, N//4 + 1)[:N]
def offether(u, bc, T):
    E = ether(len(u)); rows = []
    for _ in range(T): rows.append(u != E); u = step(u, 54, bc); E = step(E, 54, bc)
    return np.array(rows)
img = lambda A: (255*(1 - A)).astype(np.uint8)
ex = np.load('rule54_examples.npy')            # [train event, single event] from rule54_exact.py, torus N=480
single = offether(ex[1].copy(), 'periodic', 200)[40:200, 120:280]
train = offether(ex[0].copy(), 'periodic', 200)[40:200, 120:280]
# a single right mover hitting the right wall: reuse the right-moving half of the single event in a box
M = 4*40 + 1; u = ether(M); seed = ex[1][100:116].copy(); u[60:76] = seed
wall = offether(u, 'mirror', 260)[30:190, M-160:]
tiles = [img(single), img(wall), img(train)]
a = montage(tiles, cols=3, gap=6, bg=200)
write_gray('../figures/rule54_events.png', a); write_pdf('../figures/rule54_events.pdf', a)
# (b) sparse launch: a seed without a gun that keeps one mover on the torus
R = np.load('rule54_sparse.npz'); P, B = R['periodic'], R['mirror']
fin = P[:, -1, 0] + P[:, -1, 1]; gun = (fin > 10) | (B[:, -1, 0] + B[:, -1, 1] > 10)
start = P[:, 0, 0] + P[:, 0, 1]
seed = int(np.flatnonzero(~gun & (fin >= 1) & (start >= fin + 2))[0])
patch = np.random.default_rng(seed).integers(0, 2, 8)
out = []
for bc, N in (('periodic', 400), ('mirror', 401)):
    u = ether(N); u[196:204] = patch; out.append(img(offether(u, bc, 1200)[::2, :400]))
b = montage(out, cols=2, gap=8, bg=200)
write_gray('../figures/rule54_sparse.png', b); write_pdf('../figures/rule54_sparse.pdf', b)
print('seed used for the sparse figure:', seed, '; shapes', a.shape, b.shape)
print(f"sparse figure, ring: (N+, N-) at t=100 {tuple(int(x) for x in P[seed, 0, :2])}, at t=2000 {tuple(int(x) for x in P[seed, -1, :2])}; "
      f"box: at t=100 {tuple(int(x) for x in B[seed, 0, :2])}, at t=2000 {tuple(int(x) for x in B[seed, -1, :2])}")
