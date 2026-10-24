import sys, numpy as np
from pngio import write_gray, montage, upscale
a = float(sys.argv[1]) if len(sys.argv) > 1 else 0.33
N, DEC = 128, 9
def shift(u, ax, s):
    w = np.roll(u, s, ax); idx=[slice(None)]*2; src=[slice(None)]*2
    idx[ax] = 0 if s == 1 else -1; src[ax] = 1 if s == 1 else -2; w[tuple(idx)] = u[tuple(src)]; return w
def step(u):
    m = (u + shift(u,0,1) + shift(u,0,-1) + shift(u,1,1) + shift(u,1,-1))/5.0
    return np.round(np.mod(m + a, 1.0), DEC)
rng = np.random.default_rng(3); u = np.round(rng.random((N,N)), DEC); tiles = []
for t in range(1201):
    if t in (0, 50, 100, 200, 400, 600, 800, 1200):
        d = np.mod(u - shift(u,1,-1), 1.0); d = np.minimum(d, 1-d)
        tiles.append(upscale((255*(1-np.minimum(1,4*d))).astype(np.uint8), 2))
    u = step(u)
path = f'../figures/filmstrip2d_a{a}.png'
write_gray(path, montage(tiles, cols=4)); print(path)
