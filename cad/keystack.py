"""Key stack checks (D8): how far a cap can drop, and how much the frame PCB flexes.

- `cap_max_drop`: the cap is a rigid body resting on its switch nub(s). Its
  flange can rise CAP_TO_PLATE before it hits the top plate, each nub can go
  down SW_TRAVEL_MAX (switch bottomed), each down-stop foot KEY_STOP_GAP. A
  small linear program (small-angle tilt + plunge) finds the worst drop of
  any corner of the cap's bottom face relative to the frame PCB.
- `frame_deflection`: a grillage (beam lattice) model of the frame PCB's
  strips: FR-4 beams in bending and torsion, pinned at the screws. Returns the
  deflection per newton at each switch. Rough: plate action between strips,
  solder mask and the top plate's own flex are ignored.
"""

import itertools

import numpy as np

import params as P


def cap_max_drop(g: dict) -> float:
    """Worst downward travel (mm) of the cap's bottom corners, for any press."""
    G, H = [], []
    for x, y in g["nubs"]:
        G.append([1.0, x, y])
        H.append(P.SW_TRAVEL_MAX)
    for x, y in g["feet"]:
        G.append([1.0, x, y])
        H.append(P.KEY_STOP_GAP)
    for x, y in g["flange_top"]:
        G.append([-1.0, -x, -y])
        H.append(P.CAP_TO_PLATE)
    G, H = np.array(G), np.array(H)
    best = -1e9
    for tx, ty in g["bottom"]:
        for tri in itertools.combinations(range(len(G)), 3):
            A = G[list(tri)]
            if abs(np.linalg.det(A)) < 1e-9:
                continue
            v = np.linalg.solve(A, H[list(tri)])
            if np.all(G @ v <= H + 1e-9):
                best = max(best, v[0] + v[1] * tx + v[2] * ty)
    return best


def _props(w: float, t: float = P.PCB_T):
    a, b = max(w, t), min(w, t)
    J = a * b ** 3 * (1 / 3 - 0.21 * b / a * (1 - b ** 4 / (12 * a ** 4)))
    return P.FR4_E * w * t ** 3 / 12, P.FR4_G * J


def _members(rect, key_xy, win, knob_wins=(), knob_size=None):
    """Strip centerlines of the frame lattice: (horizontals, verticals) as
    (y, x0, x1, width) and (x, y0, y1, width)."""
    x0, x1, y0, y1 = rect
    rows = sorted({round(y, 3) for _, y in key_xy}, reverse=True)
    cols = sorted({round(x, 3) for x, _ in key_xy})
    w2 = win / 2
    left = min(cols) - w2
    right = max(cols) + w2
    if knob_wins:
        kw, kh = knob_size
        left = min(left, min(x for x, _ in knob_wins) - kw / 2)
        right = max(right, max(x for x, _ in knob_wins) + kw / 2)
    xl, xr = (x0 + left) / 2, (x1 + right) / 2
    hs = []
    edges = [(y1, rows[0] + w2)]                          # (upper material edge, lower)
    for a, b in zip(rows, rows[1:]):
        edges.append((a - w2, b + w2))
    if knob_wins:
        ky = knob_wins[0][1]
        edges.append((rows[-1] - w2, ky + kh / 2))
        edges.append((ky - kh / 2, y0))
    else:
        edges.append((rows[-1] - w2, y0))
    for top, bot in edges:
        hs.append(((top + bot) / 2, xl, xr, top - bot))
    key_bot = hs[len(rows)][0]                            # strip below the lowest key row
    vs = [(xl, hs[-1][0], hs[0][0], left - x0), (xr, hs[-1][0], hs[0][0], x1 - right)]
    for a, b in zip(cols, cols[1:]):
        vs.append(((a + b) / 2, key_bot, hs[0][0], (b - a) - win))
    if knob_wins:
        kxs = sorted(x for x, _ in knob_wins)
        for a, b in zip(kxs, kxs[1:]):
            vs.append(((a + b) / 2, hs[-1][0], key_bot, (b - a) - knob_size[0]))
    return hs, vs


def _snap(pt, hs, vs):
    """Project a point onto the nearest strip centerline."""
    x, y = pt
    best = None
    for yy, a, b, _ in hs:
        px = min(max(x, a), b)
        d = abs(y - yy) + abs(x - px)
        if best is None or d < best[0]:
            best = (d, (px, yy))
    for xx, a, b, _ in vs:
        py = min(max(y, a), b)
        d = abs(x - xx) + abs(y - py)
        if best is None or d < best[0]:
            best = (d, (xx, py))
    return (round(best[1][0], 3), round(best[1][1], 3))


def frame_deflection(rect, key_xy, win, supports, loads, knob_wins=(), knob_size=None) -> list[float]:
    """Deflection (mm per N) at each load point, loaded one at a time."""
    hs, vs = _members(rect, key_xy, win, knob_wins, knob_size)
    sup = [_snap(p, hs, vs) for p in supports]
    lds = [_snap(p, hs, vs) for p in loads]
    pts = set(sup) | set(lds)
    nodes = {}

    def nid(x, y):
        k = (round(x, 3), round(y, 3))
        if k not in nodes:
            nodes[k] = len(nodes)
        return nodes[k]

    lines = []
    for y, a, b, w in hs:
        xs = {a, b} | {x for x, ya, yb, _ in vs if a - 1e-6 <= x <= b + 1e-6 and ya - 1e-6 <= y <= yb + 1e-6}
        xs |= {px for px, py in pts if abs(py - round(y, 3)) < 1e-6 and a - 1e-6 <= px <= b + 1e-6}
        xs = sorted({round(v, 3) for v in xs})
        lines.append(([(x, y) for x in xs], w, True))
    for x, a, b, w in vs:
        ys = {a, b} | {y for y, xa, xb, _ in hs if xa - 1e-6 <= x <= xb + 1e-6 and a - 1e-6 <= y <= b + 1e-6}
        ys |= {py for px, py in pts if abs(px - round(x, 3)) < 1e-6 and a - 1e-6 <= py <= b + 1e-6}
        ys = sorted({round(v, 3) for v in ys})
        lines.append(([(x, y) for y in ys], w, False))
    for ln, _, _ in lines:
        for p in ln:
            nid(*p)
    n = len(nodes)
    K = np.zeros((3 * n, 3 * n))
    for ln, w, along_x in lines:
        EI, GJ = _props(w)
        bs, ts = (2, 1) if along_x else (1, 2)       # dofs: w, dw/dy, dw/dx
        for p, q in zip(ln, ln[1:]):
            L = abs(q[0] - p[0]) + abs(q[1] - p[1])
            if L < 1e-6:
                continue
            i, j = nid(*p), nid(*q)
            kb = EI / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                                         [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
            idx = [3 * i, 3 * i + bs, 3 * j, 3 * j + bs]
            K[np.ix_(idx, idx)] += kb
            idt = [3 * i + ts, 3 * j + ts]
            K[np.ix_(idt, idt)] += GJ / L * np.array([[1, -1], [-1, 1]])
    fixed = {3 * nid(*p) for p in sup}
    free = [d for d in range(3 * n) if d not in fixed]
    Kf = K[np.ix_(free, free)]
    pos = {d: k for k, d in enumerate(free)}
    out = []
    for p in lds:
        F = np.zeros(len(free))
        F[pos[3 * nid(*p)]] = 1.0
        u = np.linalg.solve(Kf, F)
        out.append(float(u[pos[3 * nid(*p)]]))
    return out
