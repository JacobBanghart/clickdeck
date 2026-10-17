"""Small CPU renderer for quick PNG previews (no OpenGL needed).

Opaque parts go through a z-buffer, then transparent parts are blended on top,
then feature edges are drawn wherever they're visible. The STEP files are the
real deliverable; these images are just for a quick look.
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


def _mesh(item: Item, tol: float):
    verts, tris = item.part.tessellate(tol, 0.3)
    v = np.array([[p.X, p.Y, p.Z] for p in verts], dtype=float)
    t = np.array(tris, dtype=int).reshape(-1, 3)
    return v, t


def _edges(item: Item):
    segs = []
    for e in item.part.edges():
        n = 2 if e.geom_type == GeomType.LINE else max(8, min(48, int(e.length * 1.5)))
        pts = e.positions([i / (n - 1) for i in range(n)])
        p = np.array([[q.X, q.Y, q.Z] for q in pts])
        segs.append(p)
    return segs


def render(items: list[Item], path: str, az: float = -60, el: float = 32,
           size: tuple[int, int] = (1500, 1000), offsets: dict[str, float] | None = None,
           tol: float = 0.15, ss: int = 2, margin: float = 0.06) -> None:
    W, H = size[0] * ss, size[1] * ss
    right, up, fwd, to_cam = _camera(az, el)
    light = np.array([-0.35, -0.55, 1.0])
    light /= np.linalg.norm(light)

    meshes = []
    for it in items:
        v, t = _mesh(it, tol)
        if offsets and it.label in offsets:
            v = v + np.array([0, 0, offsets[it.label]])
        meshes.append((it, v, t))

    allv = np.vstack([m[1] for m in meshes])
    sx, sy = allv @ right, allv @ up
    span = max((sx.max() - sx.min()) / W, (sy.max() - sy.min()) / H) / (1 - 2 * margin)
    cx, cy = (sx.max() + sx.min()) / 2, (sy.max() + sy.min()) / 2

    def project(v):
        px = (v @ right - cx) / span + W / 2
        py = H / 2 - (v @ up - cy) / span
        return px, py, v @ fwd

    zbuf = np.full((H, W), np.inf)
    img = np.tile(BG, (H, W, 1))
    transparent = []

    def raster(px, py, pz, t, colors, alpha=None, write_z=True):
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
            xs = np.arange(x0, x1 + 1) + 0.5
            ys = np.arange(y0, y1 + 1) + 0.5
            X, Y = np.meshgrid(xs, ys)
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
        lam = np.abs(n @ light)
        facing = np.abs(n @ to_cam)
        k = 0.42 + 0.45 * lam + 0.13 * facing
        return np.clip(np.outer(k, rgb), 0, 1)

    for it, v, t in meshes:
        rgba = tuple(it.color)
        rgb = np.array(rgba[:3])
        px, py, pz = project(v)
        if rgba[3] < 0.99:
            transparent.append((px, py, pz, t, shade(v, t, rgb), rgba[3]))
        else:
            raster(px, py, pz, t, shade(v, t, rgb))

    # Transparent parts: depth-tested against opaque geometry, not each other
    for px, py, pz, t, cols, a in transparent:
        raster(px, py, pz, t, cols, alpha=a * 0.7)

    # Feature edges
    for it, _, _ in meshes:
        dz = offsets.get(it.label, 0.0) if offsets else 0.0
        clear = tuple(it.color)[3] < 0.99
        col = np.array([0.25, 0.45, 0.60]) if clear else EDGE
        for seg in _edges(it):
            seg = seg + np.array([0, 0, dz])
            px, py, pz = project(seg)
            for i in range(len(seg) - 1):
                steps = int(max(abs(px[i + 1] - px[i]), abs(py[i + 1] - py[i]))) + 1
                tt = np.linspace(0, 1, steps + 1)
                xs = (px[i] + (px[i + 1] - px[i]) * tt).astype(int)
                ys = (py[i] + (py[i + 1] - py[i]) * tt).astype(int)
                zs = pz[i] + (pz[i + 1] - pz[i]) * tt
                ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
                xs, ys, zs = xs[ok], ys[ok], zs[ok]
                bias = 0.35 if not clear else 0.6
                vis = zs <= zbuf[ys, xs] + bias
                for ox, oy in ((0, 0), (1, 0), (0, 1)):
                    xx = np.clip(xs[vis] + ox, 0, W - 1)
                    yy = np.clip(ys[vis] + oy, 0, H - 1)
                    img[yy, xx] = img[yy, xx] * 0.25 + col * 0.75

    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    if ss > 1:
        out = out.resize(size, Image.LANCZOS)
    out.save(path)
