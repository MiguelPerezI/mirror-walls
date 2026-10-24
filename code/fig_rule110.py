"""Figure 4 of the article: rule 110, defect display (black where the 14-cell word centred on the cell is not
an ether word, eca.defects with the fixed ether word set), time downward, steps 1500..1999 of one run of 420 cells
from random data (default_rng(0)), ring (left) and box with mirror walls (right), same initial data.
Writes ../figures/rule110_defects_fixed.png and .pdf.   usage: python3 fig_rule110.py"""
import numpy as np
from eca import step, defects, ether_words
from pngio import write_gray, montage, upscale
from png2pdf import write_pdf
N, SEED, T0, T1, P = 420, 0, 1500, 2000, 14
ether_words(110, [1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1], 7)
tiles = []
for bc in ('periodic', 'mirror'):
    u = np.random.default_rng(SEED).integers(0, 2, N); rows = []
    for t in range(T1):
        if t >= T0: rows.append(defects(u, P, bc, 110))
        u = step(u, 110, bc)
    D = np.array(rows)
    tiles.append(upscale((255*(1 - D)).astype(np.uint8), 2))
    print(f"{bc:8s}: defect fraction over steps {T0}..{T1-1}: {D.mean():.4f}")
img = montage(tiles, cols=2, gap=8, bg=128)
write_gray('../figures/rule110_defects_fixed.png', img); write_pdf('../figures/rule110_defects_fixed.pdf', img)
print('../figures/rule110_defects_fixed.png', img.shape)
