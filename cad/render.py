"""Small CPU renderer for previews, assembly pictures and animation (no OpenGL).

Opaque parts go through a z-buffer, then transparent parts are blended on top,
then feature edges are drawn wherever they're visible. The STEP files are the
real deliverable; these images are for looking and for the assembly guide.

`Scene` tessellates every part once; `Scene.draw` then renders any subset of
parts with per-part transforms, which is what the animation needs.
"""

import math

import numpy as np
from build123d import GeomType
from PIL import Image

from model import Item

BG = np.array([0.96, 0.96, 0.97])
EDGE = np.array([0.08, 0.08, 0.09])


def _camera(az_deg: float, el_deg: float):
    az, el = math.radians(az_deg), math.radians(el_deg)
    to_cam = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    fwd = -to_cam
    up_hint = np.array([0.0, 0.0, 1.0]) if abs(el_deg) < 89 else np.array([0.0, 1.0, 0.0])
    right = np.cross(fwd, up_hint)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return right, up, fwd, to_cam


def rot_x(deg: float, pivot=(0.0, 0.0, 0.0)) -> np.ndarray:
    """4x4 rotation about an axis parallel to X through `pivot`."""
    a = math.radians(deg)
    r = np.eye(4)
    r[1:3, 1:3] = [[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]
    t, ti = np.eye(4), np.eye(4)
    t[:3, 3] = pivot
    ti[:3, 3] = -np.array(pivot)
    return t @ r @ ti


def translate(v) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = v
    return m


def tessellate(part, tol):
    """Mesh a part; if the whole shape fails (fused cables can), mesh face by face."""
    try:
        verts, tris = part.tessellate(tol, 0.3)
        return (np.array([[p.X, p.Y, p.Z] for p in verts], dtype=float),
                np.array(tris, dtype=int).reshape(-1, 3))
    except Exception:
        vs, ts, n = [], [], 0
        for f in part.faces():
            try:
                verts, tris = f.tessellate(tol, 0.3)
            except Exception:
                continue
            vs.append(np.array([[p.X, p.Y, p.Z] for p in verts], dtype=float).reshape(-1, 3))
            ts.append(np.array(tris, dtype=int).reshape(-1, 3) + n)
            n += len(verts)
        if not vs:
            return np.zeros((0, 3)), np.zeros((0, 3), dtype=int)
        return np.vstack(vs), np.vstack(ts)


class Scene:
    def __init__(self, items: list[Item], tol: float = 0.15, edges: bool = True):
        self.items = {}
        for it in items:
            v, t = tessellate(it.part, tol)
            segs = []
            if edges and not it.label.startswith("cable_"):   # cables: no seam lines
                for e in it.part.edges():
                    n = 2 if e.geom_type == GeomType.LINE else max(8, min(48, int(e.length * 1.5)))
                    pts = e.positions([i / (n - 1) for i in range(n)])
                    segs.append(np.array([[q.X, q.Y, q.Z] for q in pts]))
            self.items[it.label] = (it, v, t, segs)

    def labels(self):
        return list(self.items)

    def draw(self, labels=None, az: float = -60, el: float = 32,
             size: tuple[int, int] = (1500, 1000), transforms: dict | None = None,
             dim: set | None = None, ss: int = 2, margin: float = 0.06,
             fit_labels=None, fit_transforms: dict | None = None,
             edges: bool = True) -> Image.Image:
        """Render `labels` (default: all).

        transforms: label -> 4x4 matrix or (dx, dy, dz) offset.
        dim: labels drawn faded (to highlight the others).
        fit_labels / fit_transforms: what the view is framed on (default: what's
        drawn), so animation frames keep a steady camera.
        """
        W, H = size[0] * ss, size[1] * ss
        right, up, fwd, to_cam = _camera(az, el)
        light = np.array([-0.35, -0.55, 1.0])
        light /= np.linalg.norm(light)
        labels = list(self.items) if labels is None else [lb for lb in labels if lb in self.items]
        transforms = transforms or {}
        dim = dim or set()

        def xf(label, v, tf):
            m = tf.get(label)
            if m is None:
                return v
            if isinstance(m, np.ndarray) and m.shape == (4, 4):
                return v @ m[:3, :3].T + m[:3, 3]
            return v + np.array(m)

        fit = labels if fit_labels is None else [lb for lb in fit_labels if lb in self.items]
        ftf = transforms if fit_transforms is None else fit_transforms
        allv = np.vstack([xf(lb, self.items[lb][1], ftf) for lb in fit])
        sx, sy = allv @ right, allv @ up
        span = max((sx.max() - sx.min()) / W, (sy.max() - sy.min()) / H) / (1 - 2 * margin)
        cx, cy = (sx.max() + sx.min()) / 2, (sy.max() + sy.min()) / 2

        def project(v):
            return (v @ right - cx) / span + W / 2, H / 2 - (v @ up - cy) / span, v @ fwd

        zbuf = np.full((H, W), np.inf)
        img = np.tile(BG, (H, W, 1))

        def raster(px, py, pz, t, colors, alpha=None):
            for k, (a, b, c) in enumerate(t):
                x0 = max(int(math.floor(min(px[a], px[b], px[c]))), 0)
                x1 = min(int(math.ceil(max(px[a], px[b], px[c]))), W - 1)
                y0 = max(int(math.floor(min(py[a], py[b], py[c]))), 0)
                y1 = min(int(math.ceil(max(py[a], py[b], py[c]))), H - 1)
                if x1 < x0 or y1 < y0:
                    continue
                area = (px[b] - px[a]) * (py[c] - py[a]) - (px[c] - px[a]) * (py[b] - py[a])
                if abs(area) < 1e-9:
                    continue
                X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
                w0 = ((px[b] - X) * (py[c] - Y) - (px[c] - X) * (py[b] - Y)) / area
                w1 = ((px[c] - X) * (py[a] - Y) - (px[a] - X) * (py[c] - Y)) / area
                w2 = 1 - w0 - w1
                inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
                if not inside.any():
                    continue
                z = w0 * pz[a] + w1 * pz[b] + w2 * pz[c]
                region = zbuf[y0:y1 + 1, x0:x1 + 1]
                vis = inside & (z < region - 1e-4)
                if not vis.any():
                    continue
                target = img[y0:y1 + 1, x0:x1 + 1]
                if alpha is None:
                    target[vis] = colors[k]
                    region[vis] = z[vis]
                else:
                    target[vis] = target[vis] * (1 - alpha) + colors[k] * alpha

        def shade(v, t, rgb):
            n = np.cross(v[t[:, 1]] - v[t[:, 0]], v[t[:, 2]] - v[t[:, 0]])
            n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
            k = 0.42 + 0.45 * np.abs(n @ light) + 0.13 * np.abs(n @ to_cam)
            return np.clip(np.outer(k, rgb), 0, 1)

        transparent = []
        for lb in labels:
            it, v, t, _ = self.items[lb]
            v = xf(lb, v, transforms)
            rgba = tuple(it.color)
            rgb = np.array(rgba[:3])
            if lb in dim:
                rgb = rgb * 0.6 + 0.4 * BG
            px, py, pz = project(v)
            if rgba[3] < 0.99:
                transparent.append((px, py, pz, t, shade(v, t, rgb), rgba[3]))
            else:
                raster(px, py, pz, t, shade(v, t, rgb))
        for px, py, pz, t, cols, a in transparent:
            raster(px, py, pz, t, cols, alpha=a * 0.7)

        if edges:
            for lb in labels:
                it, _, _, segs = self.items[lb]
                clear = tuple(it.color)[3] < 0.99
                col = np.array([0.25, 0.45, 0.60]) if clear else EDGE
                if lb in dim:
                    col = col * 0.6 + 0.4 * BG
                for seg in segs:
                    seg = xf(lb, seg, transforms)
                    px, py, pz = project(seg)
                    for i in range(len(seg) - 1):
                        steps = int(max(abs(px[i + 1] - px[i]), abs(py[i + 1] - py[i]))) + 1
                        tt = np.linspace(0, 1, steps + 1)
                        xs = (px[i] + (px[i + 1] - px[i]) * tt).astype(int)
                        ys = (py[i] + (py[i + 1] - py[i]) * tt).astype(int)
                        zs = pz[i] + (pz[i + 1] - pz[i]) * tt
                        ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
                        xs, ys, zs = xs[ok], ys[ok], zs[ok]
                        vis = zs <= zbuf[ys, xs] + (0.35 if not clear else 0.6)
                        for ox, oy in ((0, 0), (1, 0), (0, 1)):
                            xx = np.clip(xs[vis] + ox, 0, W - 1)
                            yy = np.clip(ys[vis] + oy, 0, H - 1)
                            img[yy, xx] = img[yy, xx] * 0.25 + col * 0.75

        out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
        return out.resize(size, Image.LANCZOS) if ss > 1 else out


def render(items: list[Item], path: str, az: float = -60, el: float = 32,
           size: tuple[int, int] = (1500, 1000), offsets: dict[str, tuple] | None = None,
           tol: float = 0.15, ss: int = 2, margin: float = 0.06) -> None:
    """One-shot render (used by build.py previews)."""
    Scene(items, tol).draw(az=az, el=el, size=size, transforms=offsets, ss=ss,
                           margin=margin).save(path)
