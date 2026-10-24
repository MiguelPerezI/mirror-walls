"""Big space-time diagrams of the 1-D class-4 rule (a=0.398, mean of 3 + a, mod 1), Wolfram difference display.
Writes ../figures/class4_1d_a{a}_{periodic,mirror}.png and, from the mirror run, ../figures/class4_1d_wallzoom.png
(the 60 cells nearest the left wall during steps 300..600, magnified 4x; needs T >= 600).
Figure 1 of the article is python3 view1d.py 0.398 300 600 (then png2pdf.py for the PDFs).
usage: python3 view1d.py [a] [N] [T]"""
import sys, numpy as np
from pngio import write_gray, upscale
a = float(sys.argv[1]) if len(sys.argv) > 1 else 0.398
N = int(sys.argv[2]) if len(sys.argv) > 2 else 300
T = int(sys.argv[3]) if len(sys.argv) > 3 else 900
DEC = 9
ZOOM_T0, ZOOM_T1, ZOOM_W, ZOOM_S = 300, 600, 60, 4
def step(u, bc):
    L, R = np.roll(u, 1), np.roll(u, -1)
    if bc == 'mirror': L[0] = u[1]; R[-1] = u[-2]
    return np.round(np.mod((L + u + R)/3.0 + a, 1.0), DEC)
for bc in ('periodic', 'mirror'):
    rng = np.random.default_rng(1); u = np.round(rng.random(N), DEC)
    rows = []
    for t in range(T):
        d = np.mod(u - np.roll(u, -1), 1.0); d = np.minimum(d, 1-d)
        if bc == 'mirror': d[-1] = 0
        rows.append(d); u = step(u, bc)
    S = np.array(rows)
    img = (255*(1 - np.minimum(1, 3*S))).astype(np.uint8)   # black = structure, white = background
    path = f'../figures/class4_1d_a{a}_{bc}.png'
    write_gray(path, upscale(img, 3)); print(path)
    if bc == 'mirror' and T >= ZOOM_T1:
        path = '../figures/class4_1d_wallzoom.png'
        write_gray(path, upscale(img[ZOOM_T0:ZOOM_T1, :ZOOM_W], ZOOM_S)); print(path)
