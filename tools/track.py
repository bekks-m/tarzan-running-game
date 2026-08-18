#!/usr/bin/env python3
"""
Track the player across extracted frames and report camera-compensated position.

    python3 tools/track.py <framedir> [--x0 N --x1 N --y0 N --y1 N]

Prints one row per frame:
    t  screen_feet  cam_dy  world_feet  blob_height  cx

WHY CAMERA COMPENSATION: the reference capture pans vertically up to 254px during
a jump. Raw screen-Y is camera motion + character motion added together, and the
error looks entirely plausible - it just makes every jump read shorter and faster
than it is. Do not skip this step.
"""
import numpy as np, glob, re, sys, argparse
from PIL import Image
from collections import deque

def tsec(f):
    m = re.search(r"t(\d+)_(\d+)", f)
    return int(m.group(1)) + int(m.group(2)) / 1000

def components(mask, minpx=60):
    """8-connected blobs, pure numpy BFS (no scipy dependency)."""
    seen = np.zeros_like(mask); out = []; H, W = mask.shape
    for sy, sx in zip(*np.where(mask)):
        if seen[sy, sx]: continue
        q = deque([(sy, sx)]); seen[sy, sx] = True; pts = []
        while q:
            y, x = q.popleft(); pts.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; q.append((ny, nx))
        if len(pts) >= minpx: out.append(np.array(pts))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("framedir")
    ap.add_argument("--y0", type=int, default=30,   help="play area top (exclude letterbox)")
    ap.add_argument("--y1", type=int, default=700,  help="play area bottom (exclude HUD)")
    ap.add_argument("--x0", type=int, default=8)
    ap.add_argument("--x1", type=int, default=1261)
    ap.add_argument("--bg0", type=int, default=700, help="background strip for camera tracking")
    ap.add_argument("--bg1", type=int, default=1240)
    ap.add_argument("--range", type=int, default=320, help="max camera shift searched, px")
    a = ap.parse_args()

    fs = sorted(glob.glob(a.framedir + "/*.png"), key=tsec)
    if not fs: sys.exit(f"no frames in {a.framedir}")
    prof = lambda im: im[:, a.bg0:a.bg1].mean(axis=(1, 2))
    ref = prof(np.array(Image.open(fs[0]).convert("RGB")).astype(float))
    R = a.range

    def camera_dy(im):
        """Vertical camera offset, by cross-correlating static background rows."""
        p = prof(im); best, score = 0, -1e18
        for s in range(-R, R + 1):
            lo, hi = max(R, R - s), min(len(ref) - R, len(ref) - R - s)
            if hi - lo < 80: continue
            c = -((ref[lo:hi] - p[lo + s:hi + s]) ** 2).mean()
            if c > score: score, best = c, s
        return best

    print(f"{'t':>8}{'screen':>8}{'cam_dy':>8}{'world':>8}{'h':>5}{'cx':>8}")
    for f in fs:
        im = np.array(Image.open(f).convert("RGB")).astype(float)
        dy = camera_dy(im)
        sub = im[a.y0:a.y1, a.x0:a.x1].astype(int)
        r, g, b = sub[:, :, 0], sub[:, :, 1], sub[:, :, 2]
        mask = (r > 110) & (r > g + 32) & (r > b + 42) & (g >= b)   # skin tone
        cs = components(mask)
        if not cs:
            print(f"{tsec(f):8.3f}      --{dy:8d}"); continue
        p = max(cs, key=len); ys, xs = p[:, 0], p[:, 1]
        feet = int(ys.max()) + a.y0
        print(f"{tsec(f):8.3f}{feet:8d}{dy:8d}{feet - dy:8d}"
              f"{int(ys.max() - ys.min()):5d}{xs.mean() + a.x0:8.1f}")

if __name__ == "__main__":
    main()
