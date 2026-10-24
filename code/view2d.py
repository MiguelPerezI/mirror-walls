"""Live pygame viewer of the continuous CA on a box with mirror walls (or periodic).
usage: python3 view2d.py [a] [N] [mirror|periodic]      keys: space = pause, r = reseed, q = quit
Try a = 0.33 (phase walls), 0.49 (intermittent spots), 0.398 (chaos)."""
import sys, numpy as np, pygame
a = float(sys.argv[1]) if len(sys.argv) > 1 else 0.33
N = int(sys.argv[2]) if len(sys.argv) > 2 else 160
bc = sys.argv[3] if len(sys.argv) > 3 else 'mirror'
DEC, SCALE = 9, 4
def shift(u, ax, s):
    w = np.roll(u, s, ax)
    if bc == 'mirror':
        idx = [slice(None)]*2; src = [slice(None)]*2
        idx[ax] = 0 if s == 1 else -1; src[ax] = 1 if s == 1 else -2
        w[tuple(idx)] = u[tuple(src)]
    return w
def step(u):
    m = (u + shift(u,0,1) + shift(u,0,-1) + shift(u,1,1) + shift(u,1,-1))/5.0
    return np.round(np.mod(m + a, 1.0), DEC)
def display(u):
    d = np.mod(u - shift(u,1,-1), 1.0); d = np.minimum(d, 1-d)
    g = (255*(1 - np.minimum(1, 4*d))).astype(np.uint8)
    return np.repeat(np.repeat(g, SCALE, 0), SCALE, 1)
rng = np.random.default_rng(); u = np.round(rng.random((N,N)), DEC)
pygame.init(); screen = pygame.display.set_mode((N*SCALE, N*SCALE)); pygame.display.set_caption(f"a={a} {bc}  (space pause, r reseed, q quit)")
paused = False; t = 0
while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_q: pygame.quit(); sys.exit()
            if ev.key == pygame.K_SPACE: paused = not paused
            if ev.key == pygame.K_r: u = np.round(rng.random((N,N)), DEC); t = 0
    if not paused:
        u = step(u); t += 1
        g = display(u)
        surf = pygame.surfarray.make_surface(np.stack([g.T]*3, axis=-1))
        screen.blit(surf, (0,0)); pygame.display.flip()
    pygame.time.wait(20)
