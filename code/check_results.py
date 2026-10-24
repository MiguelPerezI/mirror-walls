"""Check every number quoted in main.tex against the outputs that reproduce.sh writes to results/, and the
figures of the article against the SHA-256 of the committed files. Prints PASS/FAIL per number.
  python3 check_results.py               check, exit status 1 if anything fails or is missing
  python3 check_results.py --markdown    also write results/EXPECTED.md (number in main.tex -> results file:line)
Agreement means equality at the precision printed in the article (a quoted 0.31 matches 0.305..0.315 as printed by
the script, half a unit of the last digit on each side); "about" claims allow 10 %."""
import os, re, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
RES, FIG = os.path.join(ROOT, 'results'), os.path.join(ROOT, 'figures')

class Missing(Exception): pass
_cache = {}
def lines(name):
    if name not in _cache:
        p = os.path.join(RES, name); _cache[name] = open(p).read().splitlines() if os.path.exists(p) else None
    if _cache[name] is None: raise Missing(f"results/{name} missing")
    return _cache[name]
def grab(name, pattern, after=0):
    """(line, 'name:lineno') of the first line of results/<name> matching the regex (or the line `after` lines below)"""
    L = lines(name); rx = re.compile(pattern)
    for i, l in enumerate(L):
        if rx.search(l): return L[i + after], f"{name}:{i + 1 + after}"
    raise Missing(f"no line matching {pattern!r} in results/{name}")
def find(rx, s, group=1):
    m = re.search(rx, s)
    if not m: raise Missing(f"pattern {rx!r} not found")
    return m.group(group)
def ndec(s): s = str(s); return len(s.split('.')[1]) if '.' in s else 0
def close(paper, got):
    """equal at the printed precision: |paper - got| <= half a unit of the last digit of each"""
    return abs(float(paper) - float(got)) <= 0.5*10**-ndec(paper) + 0.5*10**-ndec(got) + 1e-12
def about(paper, got, rel=0.10): return abs(float(got) - float(paper)) <= rel*abs(float(paper))

CHECKS = []   # (id, where, quoted text, paper value, function -> (reproduced, ok, [refs]))
def check(cid, where, text, paper):
    def deco(fn): CHECKS.append((cid, where, text, paper, fn)); return fn
    return deco
def todo(cid, where, text, paper, why):
    CHECKS.append((cid, where, text, paper, lambda: (why, None, [])))

# ---------------------------------------------------------------- Section 2
@check('S2.1', 'Sec. 2', 'rule 110 is not [reflection symmetric] (its mirror image is rule 124); rule 54 is', '124; 54')
def _():
    mirror = lambda r: sum(((r >> (4*l + 2*c + rr)) & 1) << (4*rr + 2*c + l) for l in (0, 1) for c in (0, 1) for rr in (0, 1))
    return f"{mirror(110)}; {mirror(54)}", (mirror(110), mirror(54)) == (124, 54), ['computed in check_results.py']

# ---------------------------------------------------------------- Section 3
@check('S3.1', 'Sec. 3', 'on 400 cells for 3000 steps in one dimension ... maximum difference ... is 0', '0')
def _():
    l, ref = grab('reflection_principle.txt', r'^1-D: max .* over 3000 steps')
    v = find(r'= ([\d.e+-]+)', l); return v, float(v) == 0, [ref]
@check('S3.2', 'Sec. 3', 'on 64^2 cells for 1000 steps in two dimensions ... maximum difference ... is 0', '0')
def _():
    l, ref = grab('reflection_principle.txt', r'^2-D: max .* over 1000 steps')
    v = find(r'= ([\d.e+-]+)', l); return v, float(v) == 0 and '(126, 126)' in l, [ref]

# ---------------------------------------------------------------- Section 4
@check('S4.1', 'Sec. 4, the zoo', 'one dominant mover, of speed 0.1 cells per step in either direction', '0.1')
def _():
    l, ref = grab('catalogue2.txt', r'^summary:'); v = find(r'mean \|v\| ([\d.]+)', l)
    return v, close('0.1', v), [ref]
@check('S4.2', 'Sec. 4, the zoo', 'width about 3.5 cells', 'about 3.5')
def _():
    l, ref = grab('catalogue2.txt', r'^summary:'); v = find(r'movers .* mean width ([\d.]+);', l); return v, about('3.5', v), [ref]
@check('S4.3', 'Sec. 4, the zoo', 'a rare slow, wider class (about 5% of tracks)', 'about 0.05')
def _():
    l, ref = grab('catalogue2.txt', r'^summary:'); v = find(r'= ([\d.]+) of tracks', l); return v, about('0.05', v), [ref]
@check('S4.4', 'Sec. 4, the zoo', 'lives about 60 steps against about 105 for the movers', 'about 60; about 105')
def _():
    l, ref = grab('slowclass2.txt', r'^periodic:'); s, f = find(r'mean life slow (\d+)', l), find(r'fast (\d+)$', l)
    return f"{s}; {f} (ring)", about('60', s) and about('105', f), [ref]
@check('S4.5', 'Sec. 4 and abstract', 'the ring and the box give 0.0723 clusters per cell per step both', '0.0723; 0.0723')
def _():
    a, r1 = grab('perstep.txt', r'^periodic:'); b, r2 = grab('perstep.txt', r'^mirror  :')
    x, y = (find(r'bulk clusters/cell/step=([\d.]+)', s) for s in (a, b)); return f"{x}; {y}", x == y == '0.0723', [r1, r2]
@check('S4.6', 'Sec. 4', 'fractions 0.406 and 0.408 of wide clusters (width at least 6)', '0.406; 0.408')
def _():
    a, r1 = grab('perstep.txt', r'^periodic:'); b, r2 = grab('perstep.txt', r'^mirror  :')
    x, y = (find(r'wide fraction=([\d.]+)', s) for s in (a, b)); return f"{x}; {y}", close('0.406', x) and close('0.408', y), [r1, r2]
@check('S4.7', 'Sec. 4', 'Mean lifetimes ... (104 against 105 steps for movers, 59 against 60 for the slow class)', '104; 105; 59; 60')
def _():
    a, r1 = grab('slowclass2.txt', r'^periodic:'); b, r2 = grab('slowclass2.txt', r'^mirror  :')
    fr, fb, sr, sb = find(r'fast (\d+)$', a), find(r'fast (\d+)$', b), find(r'slow (\d+),', a), find(r'slow (\d+),', b)
    return f"{fr}; {fb}; {sr}; {sb}", (fr, fb, sr, sb) == ('104', '105', '59', '60'), [r1, r2]
@check('S4.8', 'Sec. 4', 'Total cluster counts over 2*10^4 steps fluctuate around 30 in both geometries with no trend', 'about 30')
def _():
    out, refs, ok = [], [], True
    for bc in ('periodic', 'mirror  '):
        l, ref = grab('population.txt', rf'^{bc} clusters at t=', after=1); v = [float(x) for x in l.split()[1:]]   # t = 0 excluded
        m = sum(v)/len(v); half = len(v)//2; trend = sum(v[half:])/(len(v)-half) - sum(v[:half])/half
        out.append(f"{bc.strip()} mean {m:.1f} (range {min(v):.1f}-{max(v):.1f}, late minus early {trend:+.1f})"); refs.append(ref)
        ok &= about('30', m) and abs(trend) < 3
    return '; '.join(out), ok, refs
@check('S4.9', 'Sec. 4', 'the wall node has activity 0.09 and its neighbour 0.23 against a bulk value of 0.28', '0.09; 0.23; 0.28')
def _():
    l, ref = grab('wall1d.txt', r'^neumann'); b = find(r'bulk activity=([\d.]+)', l); c = find(r'first 12 cells: \[([^\]]+)\]', l).split()
    return f"{c[0]}; {c[1]}; {b}", close('0.09', c[0]) and close('0.23', c[1]) and close('0.28', b), [ref]
@check('S4.10', 'Sec. 4', 'a quiet layer two cells deep ... and nothing else (cells 2-11 within 0.05 of the bulk)', 'cells 2-11 at bulk')
def _():
    l, ref = grab('wall1d.txt', r'^neumann'); b = float(find(r'bulk activity=([\d.]+)', l))
    c = [float(x) for x in find(r'first 12 cells: \[([^\]]+)\]', l).split()]
    dev = max(abs(x - b) for x in c[2:]); return f"max deviation {dev:.3f}", dev < 0.05, [ref]

# ---------------------------------------------------------------- Section 5
@check('S5.1', 'Sec. 5', 'exactly one shape is found for each direction: a pair of adjacent off-ether cells, starting at residue 2 modulo 4 (right movers) or 1 modulo 4 (left movers)', 'right [2], left [1]; shape 11')
def _():
    l, ref = grab('rule54_exact.txt', r'^single-mover classes'); l2, ref2 = grab('rule54_exact.txt', r'\(single mover\)$')
    r, lf = find(r'right (\[[^\]]*\])', l), find(r'left (\[[^\]]*\])', l)
    return f"right {r}, left {lf}; {l2.strip()}", r == '[2]' and lf == '[1]' and 'residue 2 shape [1 1 0 0 0 0 0 0 0 0 0 0]' in l2, [ref, ref2]
@check('S5.2', 'Sec. 5', 'the other outcomes are trains of two or more movers four cells apart', 'trains')
def _():
    L = lines('rule54_exact.txt'); i0 = next(i for i, l in enumerate(L) if l.startswith('L=10: phase classes'))
    n = int(find(r': (\d+)$', L[i0])); cl = L[i0 + 1:i0 + 1 + n]
    tr = [find(r'\((.*)\)$', c) for c in cl]
    return '; '.join(tr), sum(t == 'single mover' for t in tr) == 1 and all(t == 'single mover' or t.startswith('train of') for t in tr), [f"rule54_exact.txt:{i0 + 1}-{i0 + 1 + n}"]
@check('S5.3', 'Sec. 5', 'A survey of every mover in 1500 random launches of 20 cells ... 3x10^5 observations ... finds no other residue', 'about 300000; residues 2 and 1')
def _():
    l, ref = grab('rule54_phases.txt', r'^summary:'); n = find(r'summary: (\d+) mover', l); res = find(r'seen: (.*)$', l)
    return f"{n}; {res}", about('300000', n) and res == 'w+ [2], w- [1]', [ref]
@check('S5.4', 'Sec. 5', 'Placing a single right and a single left mover at every admissible pair of offsets on a ring, we find one collision class ... annihilates both movers, leaving pure ether', '1 class, annihilation')
def _():
    l, ref = grab('rule54_exact.txt', r'^head-on collisions of two single movers'); return l.split(': ', 1)[1], l.endswith('1 outcome class(es): annihilation, pure ether left'), [ref]
@check('S5.5', 'Sec. 5', '[the collision] is mirror-symmetric about a node at all times', 'symmetric')
def _():
    l, ref = grab('rule54_exact.txt', r'single mover \(w\+\) vs single mover \(w-\): state mirror-symmetric'); return l.strip(), l.endswith('True'), [ref]
@check('S5.6', 'Sec. 5', 'a single right mover started at any offset in a box of length 4k+1 meets the wall in one way, and nothing is left', 'one way, nothing left')
def _():
    L = lines('rule54_exact.txt'); ev = [(i, l) for i, l in enumerate(L) if l.strip().startswith('(') and '[class ' in l]
    s = [(i, l) for i, l in ev if l.rstrip().endswith('= single mover]')]
    return '; '.join(l.strip() for _, l in s), len(s) == 1 and "'{}', 0)" in s[0][1], [f"rule54_exact.txt:{i + 1}" for i, _ in s]
@check('S5.7', 'Sec. 5', 'trains of two and three meeting the wall lose all their members', 'nothing left')
def _():
    L = lines('rule54_exact.txt'); ev = [(i, l) for i, l in enumerate(L) if l.strip().startswith('(') and '= train of' in l]
    sizes = sorted(int(find(r'train of (\d+)', l)) for _, l in ev)
    return '; '.join(l.strip() for _, l in ev), sizes == [2, 3] and all("'{}', 0)" in l for _, l in ev), [f"rule54_exact.txt:{i + 1}" for i, _ in ev]
@check('S5.8', 'Sec. 5 and Fig. 2', 'A train of four movers meeting a single mover loses one member and continues ("one pair annihilates and three continue")', 'train of 4 -> train of 3')
def _():
    l, ref = grab('rule54_exact.txt', r"single mover \(w\+\) vs train of 4 movers \(w-\)")
    return l.strip(), """{'w-': 1}", 6)""" in l, [ref]          # one w- blob of 6 off-ether cells = a train of 3 movers
@check('S5.9', 'Sec. 5', 'Of 200 patches, 110 produce a glider gun ... the other 90', '110; 90')
def _():
    l, ref = grab('rule54_sparse.txt', r'^without guns \((\d+) seeds\)'); n = int(find(r'\((\d+) seeds\)', l))
    return f"{200 - n}; {n}", n == 90, [ref]
TABLE1 = {'periodic': ['2.06', '1.17', '1.14', '1.14', '1.14', '1.14'], 'mirror': ['2.06', '0.00', '0.00', '0.00', '0.00', '0.00']}
for bc, vals in TABLE1.items():
    for k, (t, pv) in enumerate(zip((100, 300, 600, 1000, 1500, 2000), vals)):
        @check(f"T1.{'ring' if bc == 'periodic' else 'box'}.{t}", 'Table 1', f"{'ring (400 cells)' if bc == 'periodic' else 'box (401 cells)'}, mean number of movers at step {t}", pv)
        def _(bc=bc, k=k, pv=pv):
            l, ref = grab('rule54_sparse.txt', rf'^  {bc:8s}: mean movers \['); v = find(r'mean movers \[([^\]]+)\]', l).split(', ')[k]
            return v, close(pv, v), [ref]
@check('S5.10', 'Sec. 5, Table 1 caption, abstract', 'At step 2000 movers survive in 46 of the 90 rings and in none of the boxes', '46; 0')
def _():
    a, r1 = grab('rule54_sparse.txt', r'^  periodic: mean movers'); b, r2 = grab('rule54_sparse.txt', r'^  mirror  : mean movers')
    x, y = (find(r'seeds with movers at t=2000: (\d+)', s) for s in (a, b)); return f"{x}; {y}", (x, y) == ('46', '0'), [r1, r2]
@check('S5.11', 'Table 1 caption', 'In every ring the survivors move in a single direction', '90 of 90')
def _():
    l, ref = grab('rule54_sparse.txt', r'^  torus survivors: all same direction'); v = find(r'all same direction in (\d+ of \d+)', l); return v, v == '90 of 90', [ref]
@check('S5.12', 'Table 1 caption', 'N+ - N- at step 300 equals N+ - N- at step 2000 in 88 of the 90 rings', '88')
def _():
    l, ref = grab('rule54_sparse.txt', r'^  torus survivors:'); v = find(r'at t=2000 in (\d+) seeds', l); return v, v == '88', [ref]
@check('S5.13', 'Fig. 3 caption', 'The patch emits a train of four left movers and one right mover', '(N+, N-) = (1, 4)')
def _():
    l, ref = grab('fig_rule54.txt', r'^sparse figure, ring'); v = find(r'ring: \(N\+, N-\) at t=100 (\(\d+, \d+\))', l); return v, v == '(1, 4)', [ref]
@check('S5.14', 'Fig. 3 caption', 'the right mover meets the train ... and annihilates one member; the other three circulate forever', '(N+, N-) = (0, 3) at t=2000')
def _():
    l, ref = grab('fig_rule54.txt', r'^sparse figure, ring'); v = find(r'ring: .* at t=2000 (\(\d+, \d+\)); box', l); return v, v == '(0, 3)', [ref]
@check('S5.15', 'Fig. 3 caption', 'In the box every mover meets its image at a wall', '(0, 0) at t=2000')
def _():
    l, ref = grab('fig_rule54.txt', r'^sparse figure, ring'); v = find(r'box: .* at t=2000 (\(\d+, \d+\))', l); return v, v == '(0, 0)', [ref]
@check('S5.16', 'Sec. 5, dense', 'the ring carries 107+-9 movers and the box 94+-13', '107+-9; 94+-13')
def _():
    a, r1 = grab('rule54_charge.txt', r'^periodic: movers'); b, r2 = grab('rule54_charge.txt', r'^mirror: movers')
    (m1, e1), (m2, e2) = ((find(r'mean ([\d.]+)', s), find(r'\+- ([\d.]+)', s)) for s in (a, b))
    return f"{m1}+-{e1}; {m2}+-{e2}", close('107', m1) and close('9', e1) and close('94', m2) and close('13', e2), [r1, r2]

# ---------------------------------------------------------------- Section 6
@check('S6.1', 'Sec. 6', 'in one of two 1400-cell runs the ether fraction fell from 0.90 at step 5000 to 0 at step 8000', '0.90; 0')
def _():
    l, ref = grab('rule110_ether.txt', r'^box  seed 0:'); a, b = find(r' 5000:([\d.]+)', l), find(r' 8000:([\d.]+)', l)
    return f"{a}; {b}", a == '0.90' and float(b) == 0, [ref]
@check('S6.2', 'Sec. 6', 'in the other it stayed at 0.96 through step 8000', '0.96')
def _():
    l, ref = grab('rule110_ether.txt', r'^box  seed 1:'); v = [find(rf' {t}:([\d.]+)', l) for t in range(5000, 8001, 500)]
    return ' '.join(v) + ' (steps 5000..8000)', all(x == '0.96' for x in v), [ref]

# ---------------------------------------------------------------- Section 7
def scan():
    l, ref = grab('scan2d.txt', r'^all:'); pairs = [p.split(':') for p in l.split()[1:]]
    return [(float(a), float(v), v) for a, v in pairs], ref
@check('S7.1', 'Sec. 7, regimes', 'a late activity fraction ... from 0.29 near a=0.01', '0.29')
def _():
    p, ref = scan(); v = next(s for a, _, s in p if a == 0.01); return v, close('0.29', v), [ref]
@check('S7.2', 'Sec. 7, regimes', 'to 0.90-0.92 on the plateaus a in [0.34,0.43] and [0.57,0.66]', '0.90-0.92')
def _():
    p, ref = scan(); v = [x for a, x, _ in p[:-1] if 0.335 < a < 0.435 or 0.565 < a < 0.665]
    return f"{min(v):.2f}-{max(v):.2f}", min(v) >= 0.895 and max(v) <= 0.925, [ref]
@check('S7.3', 'Sec. 7, regimes', 'with dips to 0.42-0.45 near a=1/3, 1/2, 2/3', '0.42-0.45')
def _():
    p, ref = scan(); d = [min(x for a, x, _ in p[:-1] if abs(a - c) < 0.025) for c in (1/3, 1/2, 2/3)]
    return ', '.join(f"{x:.2f}" for x in d), all(0.415 <= x <= 0.455 for x in d), [ref]
@check('S7.4', 'Sec. 7, regimes', 'the one-dimensional class-4 value a=0.398 is fully chaotic in two dimensions (plateau value)', '0.90-0.92')
def _():
    p, ref = scan(); v = p[-1][2]; return v + ' (a=0.398, last entry)', 0.895 <= float(v) <= 0.925, [ref]

def strata(name, n, N, T, a, S, extra=''):
    l, ref = grab(name, rf'^n={n} N={N} T={T} a={re.escape(a)} seeds={S}: .*{extra}')
    cod = {int(c): (m, e) for c, m, e in re.findall(r'codim(\d)=([\d.]+)\+-([\d.]+)', l)}
    dist = [d.split('+-')[0] for d in find(r'\| dist0\.\.\d+: ([^|]+)', l).split()]
    return cod, dist, ref
def entry(paper, m, e):
    pm, ps = re.match(r'([\d.]+)\((\d+)\)', paper).groups(); se = int(round(float(e)*1000))
    return f"{m}({se})", pm == m and int(ps) == se
REG = {'0.398': 'chaos', '0.49': 'intermittent', '0.33': 'phase walls'}
TABLE2 = [('0.398', 2, '0.989(0) 0.948(0) 0.738(3)'), ('0.398', 3, '0.997(0) 0.993(0) 0.981(0) 0.922(3)'),
          ('0.49', 2, '0.558(2) 0.494(2) 0.196(4)'), ('0.49', 3, '0.484(5) 0.505(5) 0.506(3) 0.305(8)'),
          ('0.33', 2, '0.510(5) 0.340(3) 0.172(11)'), ('0.33', 3, '0.996(2) 0.992(5) 0.973(7) 0.860(10)')]
TABLE3 = [('0.398', 2, '0.989(0) 0.949(0) 0.745(3)'), ('0.398', 3, '0.997(0) 0.993(0) 0.981(0) 0.922(1)'),
          ('0.49', 2, '0.551(0) 0.494(0) 0.207(2)'), ('0.49', 3, '0.451(0) 0.474(0) 0.487(1) 0.309(2)'),
          ('0.33', 2, '0.561(1) 0.351(1) 0.165(6)'), ('0.33', 3, '0.999(0) 0.999(0) 0.995(0) 0.898(10)')]
for tab, rows, name, size, S in (('Table 2', TABLE2, 'strata_seeds.txt', {2: (128, 1500), 3: (32, 800)}, 8),
                                 ('Table 3', TABLE3, 'strata_gpu.txt', {2: (1024, 3000), 3: (128, 1500)}, 16)):
    for a, n, vals in rows:
        N, T = size[n]
        for c, pv in enumerate(vals.split()):
            reg = ('chaos (3-D rule)' if (a, n) == ('0.33', 3) else REG[a])
            @check(f"T{tab[-1]}.{a}.{N}^{n}.c{c}", tab, f"{reg}, a={a}, {N}^{n}, codim {c}", pv)
            def _(name=name, n=n, N=N, T=T, a=a, S=S, c=c, pv=pv):
                cod, _, ref = strata(name, n, N, T, a, S); got, ok = entry(pv, *cod[c]); return got, ok, [ref]
@check('S7.5', 'Sec. 7, first observation', 'at distance one from the nearest wall the two-dimensional activity is already 0.982 against 0.989 in the bulk', '0.982; 0.989')
def _():
    cod, d, ref = strata('strata_seeds.txt', 2, 128, 1500, '0.398', 8); return f"{d[1]}; {cod[0][0]}", d[1] == '0.982' and cod[0][0] == '0.989', [ref]
for n, (N1, T1), (N2, T2) in ((2, (128, 1500), (1024, 3000)), (3, (32, 800), (128, 1500))):
    @check(f"S7.6.{n}d", 'Sec. 7, first observation', (f"In three dimensions the values are the same to three decimals from {N1}^{n} to {N2}^{n} (chaos, a=0.398)" if n == 3 else f"in two dimensions they change by at most 0.007 from {N1}^{n} to {N2}^{n} (chaos, a=0.398)"), ('equal to 3 decimals' if n == 3 else '<= 0.007'))
    def _(n=n, N1=N1, T1=T1, N2=N2, T2=T2):
        c1, _, r1 = strata('strata_seeds.txt', n, N1, T1, '0.398', 8); c2, _, r2 = strata('strata_gpu.txt', n, N2, T2, '0.398', 16)
        d = max(round(abs(float(c1[c][0]) - float(c2[c][0])), 3) for c in c1)
        return ', '.join(f"codim{c} {c1[c][0]}/{c2[c][0]}" for c in sorted(c1)), (d == 0 if n == 3 else d <= 0.007), [r1, r2]
@check('S7.7', 'Sec. 7, second observation', 'the corner is strongly suppressed ... (0.20 against 0.56 in two dimensions', '0.20; 0.56')
def _():
    cod, _, ref = strata('strata_seeds.txt', 2, 128, 1500, '0.49', 8); return f"{cod[2][0]}; {cod[0][0]}", close('0.20', cod[2][0]) and close('0.56', cod[0][0]), [ref]
@check('S7.8', 'Sec. 7, second observation', '0.31 against 0.48 in three on 32^3 and against 0.45 on 128^3', '0.31; 0.48; 0.31; 0.45')
def _():
    c1, _, r1 = strata('strata_seeds.txt', 3, 32, 800, '0.49', 8); c2, _, r2 = strata('strata_gpu.txt', 3, 128, 1500, '0.49', 16)
    v = (c1[3][0], c1[0][0], c2[3][0], c2[0][0])
    return '; '.join(v), all(close(p, x) for p, x in zip(('0.31', '0.48', '0.31', '0.45'), v)), [r1, r2]
for st, c, p1, p2 in (('faces', 1, '0.02', '0.02'), ('edges', 2, '0.02', '0.04')):
    @check(f"S7.9.{st}", 'Sec. 7, second observation', f"the three-dimensional faces and edges sit above the bulk value: the faces by 0.02 on both boxes, the edges by 0.02 on 32^3 and 0.04 on 128^3 [{st}]", f"{p1}; {p2}")
    def _(c=c, p1=p1, p2=p2):
        c1, _, r1 = strata('strata_seeds.txt', 3, 32, 800, '0.49', 8); c2, _, r2 = strata('strata_gpu.txt', 3, 128, 1500, '0.49', 16)
        x, y = float(c1[c][0]) - float(c1[0][0]), float(c2[c][0]) - float(c2[0][0])
        return f"{x:.3f}; {y:.3f}", close(p1, f"{x:.3f}") and close(p2, f"{y:.3f}"), [r1, r2]
@check('S7.10', 'Sec. 7, second observation', 'the activity overshoots the bulk at distances 2-4 in two dimensions (0.59 against 0.55)', '0.59; 0.55')
def _():
    cod, d, ref = strata('strata_gpu.txt', 2, 1024, 3000, '0.49', 16); b = float(cod[0][0]); pk = max(d[2:5], key=float)
    over = [k for k in range(len(d)) if float(d[k]) > b + 0.01]
    return f"peak {pk} at distance {d.index(pk)}; bulk {cod[0][0]}; overshoot (> bulk + 0.01) at distances {over}", close('0.59', pk) and close('0.55', cod[0][0]) and over == [2, 3, 4], [ref]
@check('S7.11', 'Sec. 7, second observation', 'and at distance 1 in three (0.49 against 0.45)', '0.49; 0.45')
def _():
    cod, d, ref = strata('strata_gpu.txt', 3, 128, 1500, '0.49', 16); return f"{d[1]}; {cod[0][0]}", close('0.49', d[1]) and close('0.45', cod[0][0]), [ref]
@check('S7.12', 'Sec. 7, second observation', 'and relaxes within five to seven cells', '<= 7')
def _():
    out, refs, ok = [], [], True
    for n, N, T in ((2, 1024, 3000), (3, 128, 1500)):
        cod, d, ref = strata('strata_gpu.txt', n, N, T, '0.49', 16); b = float(cod[0][0])
        k = next(k for k in range(len(d)) if all(abs(float(x) - b) <= 0.01 for x in d[k:]))
        out.append(f"{n}-D within 0.01 of the bulk from distance {k}"); refs.append(ref); ok &= k <= 7
    return '; '.join(out), ok, refs
@check('S7.13', 'Sec. 7, third observation', 'the activity profile ... is 0.34, 0.38, 0.43, 0.45, 0.46, 0.47 for distances 0 to 5 on 128^2', '0.34 0.38 0.43 0.45 0.46 0.47')
def _():
    _, d, ref = strata('strata_seeds.txt', 2, 128, 1500, '0.33', 8)
    return ' '.join(d[:6]), all(close(p, x) for p, x in zip('0.34 0.38 0.43 0.45 0.46 0.47'.split(), d)), [ref]
@check('S7.14', 'Sec. 7, third observation', 'On 1024^2 the profile keeps rising, to 0.50 at distance 7, 0.53 at 16 and 0.55 at 24', '0.50; 0.53; 0.55')
def _():
    _, d, ref = strata('strata_gpu.txt', 2, 1024, 3000, '0.33', 16, extra=r'dist0\.\.39'); v = (d[7], d[16], d[24])
    return '; '.join(v), all(close(p, x) for p, x in zip(('0.50', '0.53', '0.55'), v)), [ref]
@check('S7.15', 'Sec. 7, third observation', 'and reaches the bulk value 0.56 only 35-40 cells from the wall (first distance within 0.002 of codim 0)', '0.56; 35-40')
def _():
    cod, d, ref = strata('strata_gpu.txt', 2, 1024, 3000, '0.33', 16, extra=r'dist0\.\.39'); b = float(cod[0][0])
    k = next((k for k, x in enumerate(d) if float(x) >= b - 0.002), None)
    return f"{cod[0][0]}; {k}", close('0.56', cod[0][0]) and k is not None and 35 <= k <= 40, [ref]
@check('S7.16', 'Sec. 7, third observation', '(0.51 on 128^2, 0.54 on 256^2, 0.55 on 512^2, 0.56 on 1024^2) [codim 0, a=0.33]', '0.51; 0.54; 0.55; 0.56')
def _():
    runs = [('strata_seeds.txt', 128, 1500, 8), ('strata_gpu.txt', 256, 3000, 16), ('strata_gpu.txt', 512, 3000, 16), ('strata_gpu.txt', 1024, 3000, 16)]
    got = [strata(f, 2, N, T, '0.33', S) for f, N, T, S in runs]; v = [g[0][0][0] for g in got]
    return '; '.join(v), all(close(p, x) for p, x in zip(('0.51', '0.54', '0.55', '0.56'), v)), [g[2] for g in got]
@check('S7.17', 'Sec. 7, third observation', 'while the face and corner entries are stable in the box size (range over 128^2..1024^2 at most 0.02)', 'stable')
def _():
    runs = [('strata_seeds.txt', 128, 1500, 8), ('strata_gpu.txt', 256, 3000, 16), ('strata_gpu.txt', 512, 3000, 16), ('strata_gpu.txt', 1024, 3000, 16)]
    got = [strata(f, 2, N, T, '0.33', S) for f, N, T, S in runs]; f1 = [float(g[0][1][0]) for g in got]; f2 = [float(g[0][2][0]) for g in got]
    return f"faces {min(f1):.3f}-{max(f1):.3f}, corners {min(f2):.3f}-{max(f2):.3f}", max(f1) - min(f1) <= 0.02 and max(f2) - min(f2) <= 0.02, [g[2] for g in got]
for N in (64, 96, 128):
    @check(f"S7.18.{N}", 'Sec. 7, fourth observation', f"on 64^3, 96^3 and 128^3 the faces equal the bulk, 0.999, and only the edges, 0.994-0.995, and the corners, 0.89-0.90, depart [{N}^3, a=0.33]", '0.999; 0.999; 0.994-0.995; 0.89-0.90')
    def _(N=N):
        cod, _, ref = strata('strata_gpu.txt', 3, N, 1500, '0.33', 16); v = [cod[c][0] for c in range(4)]
        return '; '.join(v), v[0] == v[1] == '0.999' and v[2] in ('0.994', '0.995') and 0.885 <= float(v[3]) < 0.905, [ref]
@check('S7.19', 'Table 3 caption', 'The strata with many nodes now have standard errors of at most 0.001 (codim 0 and 1, and 3-D codim 2; at the printed precision)', '<= 0.001')
def _():
    se, refs = [], []
    for a, n, _ in TABLE3:
        cod, _, ref = strata('strata_gpu.txt', n, 1024 if n == 2 else 128, 3000 if n == 2 else 1500, a, 16)
        se += [float(cod[c][1]) for c in ((0, 1) if n == 2 else (0, 1, 2))]; refs.append(ref)
    return f"max {max(se):.3f}", max(se) <= 0.001, refs
@check('S7.20', 'Sec. 7', 'A CuPy implementation of the same automaton ... reproduces every entry bit for bit', 'bit-identical')
def _():
    L = lines('contca_gpu.txt'); ok = sum('max|gpu-cpu| over all steps = 0.000e+00, activity mismatches = 0, equal arrays = True' in l for l in L) == 4 and any(l == 'batched 4 seeds == separate runs: True' for l in L)
    return '4 of 4 self-tests equal, batched equal' if ok else 'self-test mismatch', ok, ['contca_gpu.txt']
todo('S7.21', 'Sec. 7', 'computes a row of the table in a fraction of a second instead of about a minute on one CPU core', '<1 s vs ~1 min', 'not checked (timing; see the gpu times in results/strata_gpu.txt and results/reproduce_times.txt)')

# ---------------------------------------------------------------- figures: SHA-256 of the committed files
FIGS = {'Fig. 1': {'class4_1d_a0.398_periodic.png': '69101307455c8f8107d17f362b6412fd47e893012f72a3db9d766f2a6010897f',
                   'class4_1d_a0.398_periodic.pdf': '941818c4aa2ac347644940b9255cdb091636f56948ccb44860f681912ca4d40f',
                   'class4_1d_a0.398_mirror.png': 'df6ff42edb855cf598969d5aeefca56fd265ee6629bca0854b8412578194e95b',
                   'class4_1d_a0.398_mirror.pdf': 'a2edad6ccef12c17ea25da75d63c540b75f41d631e765bdeacb0e57a2773d05a',
                   'class4_1d_wallzoom.png': 'ce6a8277d5b7467da2d1fa73204e418f6c0517685fa282e032ae4bdff59f1695',
                   'class4_1d_wallzoom.pdf': '9852217130062a923c055170d71d839bcdd5a0375a75836f32acb3c8f1c9a404'},
        'Fig. 2': {'rule54_events.png': '5ea2bd64faa88f0c3d542db1a5710413d5da2b7f8050f17c6bb55c3039b6ec4e',
                   'rule54_events.pdf': '7935c644c4098d1a0f902ff3674fbff29bb6ff84985cc653d030f82195c4fedb'},
        'Fig. 3': {'rule54_sparse.png': '5c2ef48b01d62d6cabfbd1f19f51b151141361a7facfabb671e6680e3b3e696e',
                   'rule54_sparse.pdf': '876dfb6b1de1a55f9274440ebd95ee32bbc1a90e6683b353fc4780e19732f709'},
        'Fig. 4': {'rule110_defects_fixed.png': '2cf60da984f23b9fc3d40bfea5f0c67d3f8b95278f3474627ceb4c5c0a0cee08',
                   'rule110_defects_fixed.pdf': '0c38d4e03632d0962dadd78b1fe700048b534693f71c97d98a70f26ec7da3985'},
        'Fig. 5': {'cuts2d_spacetime.png': 'ffe1810e9f3c4d2e4019c8fd0b17a9a40d8a9ad2338cd9c946be16deea0c644c',
                   'cuts2d_spacetime.pdf': '11987242c0276ce988a7bedfe14919c408bffb15a2944d1372f095228812824b'},
        'Fig. 6': {'filmstrip2d_a0.33.png': 'bbef12f5628c119522df0073b010c09b5cef9b4d0c47f0d0bd7eb742209551e4',
                   'filmstrip2d_a0.33.pdf': '20832e3063e881f67eee334b1084fc5b6bc7cfefaeee687146e673a4e3640e7b',
                   'filmstrip2d_a0.49.png': '056dbabc2c2f32a727ab91fdfcd6ee87aa1f91ec1def1fc38ae2b2d000f79624',
                   'filmstrip2d_a0.49.pdf': 'bbf44ddd0d989ce197e1efc528e10567243d888412d6b7426b35cbbfbe69eb67'}}
PRODUCER = {'Fig. 1': 'view1d.py 0.398 300 600 + png2pdf.py', 'Fig. 2': 'rule54_exact.py 10 + fig_rule54.py', 'Fig. 3': 'rule54_sparse.py + fig_rule54.py',
            'Fig. 4': 'fig_rule110.py', 'Fig. 5': 'cuts2d.py + png2pdf.py', 'Fig. 6': 'filmstrip2d.py 0.33, 0.49 + png2pdf.py'}
for fig, files in FIGS.items():
    for f, h in files.items():
        @check(f"F{fig[-1]}.{f}", fig, f"figures/{f} regenerated by {PRODUCER[fig]}", 'sha256 ' + h[:12])
        def _(f=f, h=h):
            p = os.path.join(FIG, f)
            if not os.path.exists(p): raise Missing(f"figures/{f} missing")
            g = hashlib.sha256(open(p, 'rb').read()).hexdigest(); return 'sha256 ' + g[:12], g == h, [f"figures/{f}"]

# ---------------------------------------------------------------- run
def main():
    rows, n = [], {'PASS': 0, 'FAIL': 0, 'MISSING': 0, 'NOT CHECKED': 0}
    for cid, where, text, paper, fn in CHECKS:
        try:
            got, ok, refs = fn(); st = 'NOT CHECKED' if ok is None else 'PASS' if ok else 'FAIL'
        except (Missing, StopIteration, KeyError, IndexError, ValueError) as e:
            got, st, refs = f"({type(e).__name__}: {e})", 'MISSING', []
        n[st] += 1; rows.append((cid, where, text, paper, got, refs, st))
        print(f"{st:11s} {cid:22s} paper {paper:28s} reproduced {got}   [{', '.join(refs)}]")
    print(f"\n{len(rows)} checks: " + ', '.join(f"{v} {k}" for k, v in n.items()))
    if '--markdown' in sys.argv:
        esc = lambda s: str(s).replace('|', '\\|')
        with open(os.path.join(RES, 'EXPECTED.md'), 'w') as fh:
            fh.write("# Numbers of main.tex and where they are reproduced\n\n"
                     "Generated by `python3 code/check_results.py --markdown` from the outputs that `./reproduce.sh` writes to `results/`.\n"
                     "Status compares the number quoted in the article with the reproduced value at the printed precision\n"
                     "(figures: SHA-256 of the regenerated file against the committed one).\n\n"
                     f"Summary: {len(rows)} checks, " + ', '.join(f"{v} {k}" for k, v in n.items()) + ".\n\n"
                     "| id | where | quoted in main.tex | paper | reproduced | results file:line | status |\n|---|---|---|---|---|---|---|\n")
            for cid, where, text, paper, got, refs, st in rows:
                fh.write(f"| {cid} | {esc(where)} | {esc(text)} | {esc(paper)} | {esc(got)} | {esc(', '.join(refs))} | {st} |\n")
        print('wrote', os.path.join(RES, 'EXPECTED.md'))
    return 1 if n['FAIL'] or n['MISSING'] else 0

if __name__ == '__main__':
    sys.exit(main())
