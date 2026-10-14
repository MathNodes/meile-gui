#!/usr/bin/env python3
'''Build the background artwork for the Meile disk image (Meile-<ver>_arm64.dmg).

The window that Finder shows when the .dmg is opened is 640x420 points and is
made of:

    * assets/banner.png  - the Meile banner, painted across the top of the
                           window as branding
    * a brand-coloured arrow that points from the Meile.app icon (left) to the
                           Applications folder link (right)

The two Finder icons themselves (Meile.app and the Applications alias) are
positioned on top of this artwork by create-dmg, using the coordinates that
are baked into the image below (see --arrow-y / ICON_Y).  Keep them in sync
with the create-dmg call in codesign.sh.

Two files are written, background.png (1x) and background@2x.png (2x).  The
caller combines them into a multi-resolution TIFF with

    tiffutil -cathidpicheck background.png background@2x.png -out background.tiff

which is what Finder needs in order to draw the background crisply on a
Retina display.

Usage:
    make_dmg_background.py --banner assets/banner.png --out-dir assets/dmg \
                           [--width 640] [--height 420] [--arrow-y 322]
'''

import argparse
import os
from collections import Counter

from PIL import Image
from PIL import ImageDraw

# Pillow 10 moved the resampling constants into Image.Resampling
LANCZOS = getattr(Image, "Resampling", Image).LANCZOS

# Defaults; they must match the create-dmg arguments in codesign.sh.
# ICON_Y is kept high enough that the icon captions ("Meile" / "Applications")
# stay clear of the Finder window's title bar and bottom status bar.
WIDTH = 640          # window width, in points
HEIGHT = 420         # window height, in points
ICON_Y = 290         # vertical centre of the app icon / Applications link
ICON_SIZE = 100      # create-dmg --icon-size

# Arrow geometry (points), centred on ICON_Y
ARROW_TAIL_X = 256
ARROW_TIP_X = 384
ARROW_SHAFT = 4      # half thickness of the shaft
ARROW_HEAD_LEN = 20
ARROW_HEAD_HALF = 14

# Fallback brand gold, used when the banner has no gold in it
GOLD_FALLBACK = (250, 182, 27)


def background_color(banner):
    '''The banner's dominant colour - the artwork is painted with this so the
    generated image has no visible seam around the banner.'''
    return Counter(banner.convert("RGB").getdata()).most_common(1)[0][0]


def brand_color(banner, bg):
    '''The banner's accent colour (the gold of the Meile mark), used for the
    arrow.  Falls back to GOLD_FALLBACK when the banner has no colour in it.'''
    counts = Counter(p for p in banner.convert("RGB").getdata() if p != bg)
    for colour, _ in counts.most_common(50):
        if max(colour) - min(colour) >= 60:   # saturated enough to be the brand
            return colour
    return GOLD_FALLBACK


def arrow_points(icon_y, tail_x, tip_x, shaft, head_len, head_half):
    top = icon_y - shaft
    bottom = icon_y + shaft
    head_x = tip_x - head_len
    return [
        (tail_x, top),
        (head_x, top),
        (head_x, icon_y - head_half),
        (tip_x, icon_y),
        (head_x, icon_y + head_half),
        (head_x, bottom),
        (tail_x, bottom),
    ]


def build(banner, points, bg, gold, out_w, out_h):
    '''Render one resolution of the window artwork.'''
    canvas = Image.new("RGBA", (out_w, out_h), bg + (255,))

    # Branding: banner scaled to the window width, pinned to the top of the
    # window.  Both it and the canvas share the banner's background colour, so
    # the two blend together invisibly.
    banner_h = max(1, round(banner.height * out_w / banner.width))
    canvas.alpha_composite(
        banner.resize((out_w, banner_h), LANCZOS).convert("RGBA"), (0, 0)
    )

    # Arrow, drawn super-sampled so the 1x image stays smooth as well
    scale = out_w / WIDTH
    pts = [(x * scale, y * scale) for x, y in points]
    pad = 4 * scale
    x0 = int(min(p[0] for p in pts) - pad)
    y0 = int(min(p[1] for p in pts) - pad)
    x1 = int(max(p[0] for p in pts) + pad) + 1
    y1 = int(max(p[1] for p in pts) + pad) + 1

    ss = 4  # super-sampling factor for the arrow
    overlay = Image.new("RGBA", ((x1 - x0) * ss, (y1 - y0) * ss), (0, 0, 0, 0))
    ImageDraw.Draw(overlay).polygon(
        [((px - x0) * ss, (py - y0) * ss) for px, py in pts],
        fill=gold + (255,),
    )
    canvas.alpha_composite(overlay.resize((x1 - x0, y1 - y0), LANCZOS), (x0, y0))

    return canvas.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--banner", required=True, help="path to assets/banner.png")
    parser.add_argument("--out-dir", required=True, help="where to write the artwork")
    parser.add_argument("--width", type=int, default=WIDTH)
    parser.add_argument("--height", type=int, default=HEIGHT)
    parser.add_argument("--arrow-y", type=int, default=ICON_Y,
                        help="vertical centre of the Finder icons (create-dmg)")
    args = parser.parse_args()

    banner = Image.open(args.banner).convert("RGB")
    bg = background_color(banner)
    gold = brand_color(banner, bg)
    points = arrow_points(args.arrow_y, ARROW_TAIL_X, ARROW_TIP_X,
                          ARROW_SHAFT, ARROW_HEAD_LEN, ARROW_HEAD_HALF)

    os.makedirs(args.out_dir, exist_ok=True)

    # 1x for non-Retina, 2x for Retina; the DPI values keep both at the same
    # physical size, which is what tiffutil -cathidpicheck expects.
    build(banner, points, bg, gold,
          args.width * 2, args.height * 2).save(
        os.path.join(args.out_dir, "background@2x.png"), dpi=(144, 144)
    )
    build(banner, points, bg, gold,
          args.width, args.height).save(
        os.path.join(args.out_dir, "background.png"), dpi=(72, 72)
    )

    print("wrote %s/background.png (%dx%d) and background@2x.png (%dx%d)"
          % (args.out_dir, args.width, args.height,
             args.width * 2, args.height * 2))


if __name__ == "__main__":
    main()
