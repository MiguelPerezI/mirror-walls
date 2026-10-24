"""Convert the 8-bit grayscale PNGs written by pngio.py (filter 0) into vector PDFs:
each maximal run of equal cells (merged over identical consecutive rows) becomes one filled rectangle,
so the figure is crisp at any zoom. usage: python3 png2pdf.py in.png [in2.png ...]  -> same name .pdf"""
import sys, zlib, struct, numpy as np

def read_png(path):
    d = open(path, 'rb').read(); assert d[:8] == b'\x89PNG\r\n\x1a\n'
    p = 8; idat = b''
    while p < len(d):
        n = struct.unpack('>I', d[p:p+4])[0]; t = d[p+4:p+8]; c = d[p+8:p+8+n]; p += 12 + n
        if t == b'IHDR': w, h, bd, ct = struct.unpack('>IIBB', c[:10]); assert bd == 8 and ct == 0, "8-bit gray only"
        elif t == b'IDAT': idat += c
    raw = zlib.decompress(idat); rows = np.frombuffer(raw, np.uint8).reshape(h, w+1)
    assert (rows[:, 0] == 0).all(), "only filter type 0 supported"
    return rows[:, 1:].copy()

def write_pdf(path, a, cell=1.0):
    h, w = a.shape; ops = []
    y = 0
    while y < h:
        y2 = y + 1
        while y2 < h and np.array_equal(a[y2], a[y]): y2 += 1      # identical consecutive rows
        row = a[y]; x = 0; H = (y2 - y)*cell; Y = (h - y2)*cell
        while x < w:
            v = row[x]; x2 = x + 1
            while x2 < w and row[x2] == v: x2 += 1
            if v != 255:   # white background is the page
                ops.append(f"{v/255:.3f} g {x*cell:.2f} {Y:.2f} {(x2-x)*cell:.2f} {H:.2f} re f")
            x = x2
        y = y2
    content = ("1 1 1 rg 0 0 %.2f %.2f re f\n" % (w*cell, h*cell) + "\n".join(ops)).encode()
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w*cell:.2f} {h*cell:.2f}] /Contents 4 0 R >>".encode(),
            b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(zlib.compress(content, 9)) + zlib.compress(content, 9) + b"\nendstream"]
    out = b"%PDF-1.4\n"; offs = []
    for i, o in enumerate(objs, 1):
        offs.append(len(out)); out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode() + b"".join(f"{o:010d} 00000 n \n".encode() for o in offs)
    out += f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    open(path, 'wb').write(out); return len(ops), len(out)

if __name__ == '__main__':
    for f in sys.argv[1:]:
        a = read_png(f); n, size = write_pdf(f[:-4] + '.pdf', a)
        print(f"{f}: {a.shape[1]}x{a.shape[0]} -> {n} rectangles, {size/1e6:.2f} MB")
