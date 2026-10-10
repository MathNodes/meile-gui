'''Helpers to resolve and cache the logo image for a payment currency.

The logo used as the centre overlay of a payment QR code is taken from the
``icon`` field of the CoinStats price response returned by
:class:`coin_api.get_price.GetPriceAPI`.  Every time the price API is queried
(e.g. when the user picks a coin from a drop-down) the ``icon`` URL is
remembered here through :func:`remember_icon_url`.

When a NOWPayments invoice is generated the remembered URL is downloaded once
and cached as a PNG that can be pasted onto the QR code.  Network, download
and decoding errors are swallowed on purpose so that payment processing is
never interrupted by a missing logo.
'''

import hashlib
import re
from io import BytesIO
from os import path, makedirs

import requests

from conf.meile_config import MeileGuiConfig


LOGO_TIMEOUT = 10  # seconds
DEFAULT_LOGO_SIZE = 256  # px

# currency (lower case) -> remote icon URL, remembered from the price API.
_ICON_URL_CACHE = {}
# icon URL -> local cached PNG path.
_LOGO_PATH_CACHE = {}
_LOGOS_DIR = None


def _logos_dir():
    '''Return (and create if needed) the directory used to cache logos.'''
    global _LOGOS_DIR
    if _LOGOS_DIR is None:
        base = path.join(MeileGuiConfig.BASEDIR, 'img', 'nowlogos')
        if not path.isdir(base):
            makedirs(base, exist_ok=True)
        _LOGOS_DIR = base
    return _LOGOS_DIR


def _sanitize(currency):
    return re.sub(r'[^0-9A-Za-z]+', '_', str(currency)).strip('_') or 'coin'


def remember_icon_url(currency, url):
    '''Remember the remote ``icon`` URL returned by the price API.

    Called with the coin identifier exactly as supplied to the price API so
    that :func:`get_icon_url` can later resolve it (e.g. for the NOWPayments
    QR code).
    '''
    if not currency or not url:
        return
    _ICON_URL_CACHE[str(currency).strip().lower()] = url


def get_icon_url(currency):
    '''Return the remembered icon URL for ``currency`` (or ``None``).'''
    if not currency:
        return None
    return _ICON_URL_CACHE.get(str(currency).strip().lower())


def _rasterize_svg(data, size):
    '''Rasterise raw SVG bytes to PNG bytes using cairosvg (if present).'''
    try:
        import cairosvg
    except Exception as e:
        print(f"cairosvg unavailable, skipping logo rendering: {e}")
        return None
    try:
        return cairosvg.svg2png(
            bytestring=data,
            output_width=size,
            output_height=size,
        )
    except Exception as e:
        print(f"Error rasterising SVG logo: {e}")
        return None


def get_currency_logo_path(currency, logo_url=None, size=DEFAULT_LOGO_SIZE):
    '''Download, cache and return the logo for a currency.

    ``logo_url`` may be supplied explicitly in which case the remembered icon
    URL is ignored.  Otherwise the URL previously stored by
    :func:`remember_icon_url` is used.  Returns the path of a cached PNG file,
    or ``None`` when no logo is available.  Errors are swallowed on purpose.
    '''
    logo_url = logo_url or get_icon_url(currency)
    if not logo_url:
        return None

    if logo_url in _LOGO_PATH_CACHE:
        return _LOGO_PATH_CACHE[logo_url]

    # A short hash of the URL is part of the file name so a logo downloaded
    # for a previous URL of the same currency never masks a fresh one.
    digest = hashlib.md5(logo_url.encode('utf-8')).hexdigest()[:10]
    out_path = path.join(
        _logos_dir(), 'icon_' + _sanitize(currency) + '_' + digest + '.png'
    )
    if path.exists(out_path):
        _LOGO_PATH_CACHE[logo_url] = out_path
        return out_path

    try:
        response = requests.get(logo_url, timeout=LOGO_TIMEOUT)
        response.raise_for_status()
        data = response.content
    except Exception as e:
        print(f"Error downloading coin logo {logo_url}: {e}")
        return None

    if path.splitext(logo_url.split('?')[0])[1].lower() == '.svg':
        png_data = _rasterize_svg(data, size)
    else:
        png_data = data

    if not png_data:
        return None

    try:
        from PIL import Image
        logo = Image.open(BytesIO(png_data)).convert('RGBA')
        logo.save(out_path)
    except Exception as e:
        print(f"Error saving coin logo for {currency}: {e}")
        return None

    _LOGO_PATH_CACHE[logo_url] = out_path
    return out_path