#!/usr/bin/env python3
'''Build the background artwork for the Meile disk image (Meile-<ver>_arm64.dmg).

The window that Finder shows when the .dmg is opened is 640x420 points and is
made of:

    * assets/banner.png  - the Meile banner, painted across the top of the
                           window as branding
    * a brand-coloured arrow that points from the Meile.app icon (left) to the
                           Applications folder link (right)
    * a light plate behind each icon caption ("Meile" / "Applications"), see
                           CAPTION_Y / --caption below

The two Finder icons themselves (Meile.app and the Applications alias) are
positioned on top of this artwork by create-dmg, using the coordinates that
are baked into the image below (see --arrow-y / ICON_Y).  Keep them in sync
with the create-dmg call in codesign.sh.

Why the caption plates exist: Finder draws the icon captions itself, and for
any icon view with a custom background it hard-codes near-black label text -
it ignores Dark Mode and the actual brightness of the artwork.  There is no
hook for it: the Finder AppleScript dictionary's "icon view options" only
exposes arrangement / icon size / text size / label position / background
picture / background colour, and the .DS_Store icvp blob has no text colour
key either.  So the only way to keep the dark artwork and have legible
captions is to paint a light backing under the text.

Two files are written, background.png (1x) and background@2x.png (2x).  The
caller combines them into a multi-resolution TIFF with

    tiffutil -cathidpicheck background.png background@2x.png -out background.tiff

which is what Finder needs in order to draw the background crisply on a
Retina display.

Usage:
    make_dmg_background.py --banner assets/banner.png --out-dir assets/dmg \
                           [--width 640] [--height 420] [--arrow-y 322] \
                           [--caption 190:Meile] [--caption 450:Applications] \
                           [--caption-y 386]
'''

import argparse
import os
from collections import Counter

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter
from PIL import ImageFont

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

# Caption backing plates (points).  Finder draws the captions in near-black
# text as soon as the icon view has a custom background picture, so the artwork
# carries a light plate behind each caption - see the module docstring.
CAPTION_Y = 357          # vertical centre of Finder's caption text
CAPTION_TEXT_SIZE = 14   # create-dmg --text-size
CAPTION_PAD_X = 8        # horizontal padding around the caption text
CAPTION_PAD_Y = 4        # vertical padding around the caption text
CAPTION_CORNER = 5       # corner radius of the plate
CAPTION_FEATHER = 1.5    # softness of the plate edge
CAPTION_FILL = (255, 255, 255, 235)

# Fonts used to measure the captions, best match first.  Only the metrics
# matter, Finder renders the text itself.
CAPTION_FONTS = (
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Geneva.ttf",
)
CAPTION_AVG_GLYPH = 0.58   # width guess when no system font can be loaded


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


def caption_font(size):
    '''Font used only to measure the captions; Finder renders the text itself.'''
    for path in CAPTION_FONTS:
        if not os.path.exists(path):
            continue
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return None


def caption_width(font, text):
    '''Rendered width of a caption, in points.'''
    if font is not None:
        try:
            return font.getlength(text)
        except (AttributeError, NotImplementedError):
            pass
    return CAPTION_AVG_GLYPH * CAPTION_TEXT_SIZE * len(text)


def draw_captions(canvas, captions, caption_y, scale):
    '''Paint a light, softly feathered plate behind each Finder caption.

    Finder draws the caption text itself, in near-black, so this plate is what
    makes the captions readable on top of the dark artwork.
    '''
    if not captions:
        return
    font = caption_font(CAPTION_TEXT_SIZE)
    height = CAPTION_TEXT_SIZE + 2 * CAPTION_PAD_Y
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for centre_x, text in captions:
        width = caption_width(font, text) + 2 * CAPTION_PAD_X
        draw.rounded_rectangle(
            [(centre_x - width / 2.0) * scale, (caption_y - height / 2.0) * scale,
             (centre_x + width / 2.0) * scale, (caption_y + height / 2.0) * scale],
            radius=CAPTION_CORNER * scale,
            fill=CAPTION_FILL,
        )
    canvas.alpha_composite(
        overlay.filter(ImageFilter.GaussianBlur(CAPTION_FEATHER * scale))
    )


def build(banner, points, captions, caption_y, bg, gold, out_w, out_h):
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

    # Caption plates, so Finder's near-black captions stay readable
    draw_captions(canvas, captions, caption_y, scale)

    return canvas.convert("RGB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--banner", required=True, help="path to assets/banner.png")
    parser.add_argument("--out-dir", required=True, help="where to write the artwork")
    parser.add_argument("--width", type=int, default=WIDTH)
    parser.add_argument("--height", type=int, default=HEIGHT)
    parser.add_argument("--arrow-y", type=int, default=ICON_Y,
                        help="vertical centre of the Finder icons (create-dmg)")
    parser.add_argument("--caption", action="append", default=[], metavar="X:TEXT",
                        help="paint a legibility plate for the Finder caption TEXT "
                             "centred on X (repeatable)")
    parser.add_argument("--caption-y", type=int, default=CAPTION_Y,
                        help="vertical centre of the Finder caption text")
    args = parser.parse_args()

    banner = Image.open(args.banner).convert("RGB")
    bg = background_color(banner)
    gold = brand_color(banner, bg)
    points = arrow_points(args.arrow_y, ARROW_TAIL_X, ARROW_TIP_X,
                          ARROW_SHAFT, ARROW_HEAD_LEN, ARROW_HEAD_HALF)

    captions = []
    for spec in args.caption:
        centre_x, _, text = spec.partition(":")
        if not text:
            parser.error("--caption expects X:TEXT, got %r" % spec)
        captions.append((float(centre_x), text))

    os.makedirs(args.out_dir, exist_ok=True)

    # 1x for non-Retina, 2x for Retina; the DPI values keep both at the same
    # physical size, which is what tiffutil -cathidpicheck expects.
    build(banner, points, captions, args.caption_y, bg, gold,
          args.width * 2, args.height * 2).save(
        os.path.join(args.out_dir, "background@2x.png"), dpi=(144, 144)
    )
    build(banner, points, captions, args.caption_y, bg, gold,
          args.width, args.height).save(
        os.path.join(args.out_dir, "background.png"), dpi=(72, 72)
    )

    print("wrote %s/background.png (%dx%d) and background@2x.png (%dx%d)"
          % (args.out_dir, args.width, args.height,
             args.width * 2, args.height * 2))


if __name__ == "__main__":
    main()
