import numpy as np
from contca import step, active
from pngio import write_gray, montage
N, T = 160, 600
tiles=[]; 
for a in (0.125, 0.2, 0.25, 0.375, 0.4, 0.5, 0.6, 0.75):
    u = np.zeros(N); u[N//2] = 0.5
    st = np.zeros((T, N)); acts=[]; widths=[]
    for t in range(T):
        st[t]=u; A=active(u,'periodic'); widths.append(int(A.sum()))
        u = step(u, a, 1/3, 'periodic')
    print(f"a={a:5.3f}  active width at t=100,300,599: {widths[100]:3d} {widths[300]:3d} {widths[599]:3d}   "
          f"values near seed at t=599: {np.round(st[-1][N//2-3:N//2+4],3)}")
    tiles.append((255*(1-st[::2])).astype(np.uint8))   # 300 rows x 160
write_gray('../figures/cand1d.png', montage(tiles, cols=4))
