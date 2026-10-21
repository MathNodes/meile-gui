import qrcode

from PIL import Image
from PIL import ImageDraw, ImageFont
from PIL import ImageOps

from os import path

import tempfile

from conf.meile_config import MeileGuiConfig

from typedef.konstants import MeileColors

from utils.nowcurrencies import get_currency_logo_path


class QRCode():
    IMGDIR = None
    BASEDIR = None
    MeileConfig = None

    def __init__(self):
        self.BASEDIR     = MeileGuiConfig.BASEDIR
        self.IMGDIR      = MeileGuiConfig.IMGDIR
        self.MeileConfig = MeileGuiConfig()
        
    def _font(self, name, fontSize):
        '''A font of the application at ``fontSize``, never an exception.

        MeileGuiConfig.resource_path() resolves into the frozen bundle
        (sys._MEIPASS) once packaged and next to conf/meile_config.py while the
        application runs from a checkout - a directory that holds neither
        "fonts" nor "utils/fonts".  The font is therefore looked up next to
        this module first (src/utils/fonts in a checkout, <bundle>/utils/fonts
        when packaged) and PIL's built-in font is used when no candidate
        exists, so a missing font can never blank out a QR code.
        '''
        here = path.dirname(path.abspath(__file__))
        candidates = [
            path.join(here, 'fonts', name),
            self.MeileConfig.resource_path('utils/fonts/' + name),
            self.MeileConfig.resource_path('fonts/' + name),
            self.MeileConfig.resource_path('../utils/fonts/' + name),
            self.MeileConfig.resource_path('../fonts/' + name),
        ]
        for candidate in candidates:
            if not path.exists(candidate):
                continue
            try:
                return ImageFont.truetype(candidate, fontSize)
            except Exception as e:
                print("QR font %s unusable: %s" % (candidate, e))
        print("QR font %s not found, using the default font" % name)
        return ImageFont.load_default()


    def generate_wg_qr_code(self, conf_path, label=None):

        
        with open(conf_path, 'r') as f:
            wg_config = f.read().strip()
            
        wg_config = wg_config.replace("127.0.0.1,", "")

        if not label:
            label = path.basename(conf_path)

        robotoFont = self._font(path.basename(MeileColors.FONT_FACE), 13)
   
        wg_logo_path = self.MeileConfig.resource_path(MeileColors.WIREGUARD_ICON)
        has_logo = path.exists(wg_logo_path)

        QRcode = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H
        )
        QRcode.add_data(wg_config)
        QRcode.make()

        QRimg = QRcode.make_image(
            fill_color='Black', back_color='white'
        ).convert('RGB')

        if has_logo:
            logo = Image.open(wg_logo_path)
            basewidth = 100
            wpercent = (basewidth / float(logo.size[0]))
            hsize = int(float(logo.size[1]) * float(wpercent))
            logo = logo.resize((basewidth, hsize))

            pos = (
                (QRimg.size[0] - logo.size[0]) // 2,
                (QRimg.size[1] - logo.size[1]) // 2,
            )
            QRimg.paste(logo, pos)


        border = (0, 4, 0, 30)  
        QRimg = ImageOps.crop(QRimg, border)

        if len(label) <= 50:
            fontSize = 16
        elif len(label) <= 75:
            fontSize = 12
        else:
            fontSize = 11

        background = Image.new(
            'RGBA',
            (QRimg.size[0], QRimg.size[1] + 15),
            (255, 255, 255, 255),
        )
        robotoFont = self._font('Roboto-BoldItalic.ttf', fontSize)

        draw = ImageDraw.Draw(background)
        _, _, w, h = draw.textbbox((0, 0), text=str(label), font=robotoFont)
        draw.text(
            ((QRimg.size[0] + 15 - w) / 2, QRimg.size[1] - 2),
            label,
            (0, 0, 0),
            font=robotoFont,
        )

        background.paste(QRimg, (0, 0))

        safe_name = path.splitext(path.basename(conf_path))[0]
        out_path = path.join(self.IMGDIR, safe_name + '_wg.png')
        background.save(out_path)
        return out_path

    def generate_qr_code(self, ADDRESS, coin):
        DepositCoin    = coin
        DepositAddress = ADDRESS 
        
        coinLogo = self.MeileConfig.resource_path('utils/coinimg/' + DepositCoin + '.png')
        logo = Image.open(coinLogo)
        basewidth = 100
         
        # adjust image size
        wpercent = (basewidth/float(logo.size[0]))
        hsize = int((float(logo.size[1])*float(wpercent)))
        logo = logo.resize((basewidth, hsize))
        
        QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        QRcode.add_data(DepositAddress)
        QRcode.make()

        QRimg = QRcode.make_image(fill_color='Black', back_color="white").convert('RGB')
         
        # set size of QR code
        pos = ((QRimg.size[0] - logo.size[0]) // 2,
               (QRimg.size[1] - logo.size[1]) // 2)
        
        QRimg.paste(logo, pos)
        
        # crop a bit
        border = (0, 4, 0, 30) # left, top, right, bottom
        QRimg = ImageOps.crop(QRimg, border)
        
        
        # Next Process is adding and centering the Deposit address on the image
        # Creating a background a little larger and pasting the QR
        # Image onto it with the text
        if len(DepositAddress) <= 50:
            fontSize = 13
        elif len(DepositAddress) <=75:
            fontSize = 12
        else:
            fontSize = 11
            
        background = Image.new('RGBA', (QRimg.size[0], QRimg.size[1] + 15), (255,255,255,255))
        #robotoFont = ImageFont.truetype(pkg_resources.resource_filename(__name__, os.path.join('fonts', 'Roboto-BoldItalic.ttf')), fontSize)
        robotoFont = self._font('Roboto-BoldItalic.ttf', fontSize)
    
        draw = ImageDraw.Draw(background)
        
        # The caption has to be centred with the metrics of the font it is
        # drawn with (the default font metrics would put it off centre).
        _, _, w, h = draw.textbbox((0, 0), text=str(DepositAddress), font=robotoFont)
        draw.text(((QRimg.size[0]+15 - w)/2,QRimg.size[1]-2),DepositAddress, (0,0,0), font=robotoFont)
        
        background.paste(QRimg, (0,0))

        # eCryptFS (the filesystem of the encrypted data volume) rejects file
        # names longer than 143 characters, so wallet URIs and config strings
        # are sanitised and truncated before they are used as a file name -
        # generate_payment_qr_code() does the same for its output.  Short
        # alphanumeric addresses keep their name because
        # get_qr_code_address() looks the wallet QR code up as
        # "<address>.png".
        name = ADDRESS[:5] if ADDRESS.startswith(("vmess", "vless")) else ADDRESS
        safe_name = ''.join(c if c.isalnum() else '_' for c in name)[:100]
        out_path = path.join(self.IMGDIR, safe_name + ".png")
        background.save(out_path)
        return out_path

    def generate_payment_qr_code(self, ADDRESS, coin=None, logo_path=None):
        '''Generate a QR code for a payment address.

        Unlike :meth:`generate_qr_code` this routine does not require the
        coin logo asset to be present, so it also works for coins that do
        not ship an icon with the application (e.g. NOWPayments currencies).

        The logo used as an overlay is resolved in the following order:

        1. an explicit ``logo_path`` (e.g. a logo already downloaded from the
           CoinStats icon URL for a NOWPayments currency),
        2. a coin icon bundled with the application (``utils/coinimg``),
        3. the icon URL returned by the CoinStats price API and remembered
           when ``coin`` was selected (see :mod:`utils.nowcurrencies`).
        '''
        coinLogo = logo_path

        if not (coinLogo and path.exists(coinLogo)) and coin:
            bundled = self.MeileConfig.resource_path('utils/coinimg/' + coin + '.png')
            if path.exists(bundled):
                coinLogo = bundled

        if not (coinLogo and path.exists(coinLogo)) and coin:
            # Coins without a bundled icon (most NOWPayments currencies) can
            # fall back to the CoinStats icon remembered for the currency.
            try:
                coinLogo = get_currency_logo_path(coin)
            except Exception as e:
                print(f"Error resolving NOWPayments logo for {coin}: {e}")
                coinLogo = None

        QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        QRcode.add_data(ADDRESS)
        QRcode.make()

        QRimg = QRcode.make_image(fill_color='Black', back_color="white").convert('RGB')

        # The logo is decoration only: an icon file that cannot be opened must
        # not cost the payment QR code, and the logo never covers more than a
        # fifth of the code (ERROR_CORRECT_H restores what it covers).
        if coinLogo and path.exists(coinLogo):
            try:
                logo = Image.open(coinLogo)
                basewidth = max(24, min(100, int(QRimg.size[0] * 0.2)))
                wpercent = (basewidth / float(logo.size[0]))
                hsize = max(1, int((float(logo.size[1]) * float(wpercent))))
                logo = logo.resize((basewidth, hsize))
                pos = (
                    (QRimg.size[0] - logo.size[0]) // 2,
                    (QRimg.size[1] - logo.size[1]) // 2,
                )
                if logo.mode in ('RGBA', 'LA') or (logo.mode == 'P' and 'transparency' in logo.info):
                    logo = logo.convert('RGBA')
                    QRimg.paste(logo, pos, logo)
                else:
                    QRimg.paste(logo, pos)
            except Exception as e:
                print("QR logo %s skipped: %s" % (coinLogo, e))

        # crop a bit
        border = (0, 4, 0, 30)  # left, top, right, bottom
        QRimg = ImageOps.crop(QRimg, border)

        if len(ADDRESS) <= 50:
            fontSize = 13
        elif len(ADDRESS) <= 75:
            fontSize = 12
        else:
            fontSize = 11

        background = Image.new('RGBA', (QRimg.size[0], QRimg.size[1] + 15), (255, 255, 255, 255))
        robotoFont = self._font('Roboto-BoldItalic.ttf', fontSize)

        draw = ImageDraw.Draw(background)
        # The caption is the wallet URI, which is a lot wider than the QR code
        # itself (a BOLT11 invoice alone is ~250 characters), so it is
        # shortened until it fits the image - a caption wider than the image
        # would leave a wide white strip next to the code in the dialog.  The
        # complete address/URI is the text field of the dialog.
        caption = str(ADDRESS)
        try:
            while len(caption) > 8:
                if draw.textbbox((0, 0), caption + '...', font=robotoFont)[2] <= QRimg.size[0] - 10:
                    break
                caption = caption[:-1]
        except Exception as e:
            print("QR caption could not be measured: %s" % e)
            caption = str(ADDRESS)[:32]
        if caption != str(ADDRESS):
            caption = caption + '...'
        _, _, w, h = draw.textbbox((0, 0), text=caption, font=robotoFont)
        draw.text(((QRimg.size[0] + 15 - w) / 2, QRimg.size[1] - 2), caption, (0, 0, 0), font=robotoFont)

        background.paste(QRimg, (0, 0))

        # eCryptFS rejects file names longer than 143 characters, prefix and
        # ".png" included (see generate_qr_code), so the URI is cut down to
        # 100 characters - the QR code itself still carries all of it.
        safe_name = ''.join(c if c.isalnum() else '_' for c in ADDRESS)[:100]
        out_path = path.join(self.IMGDIR, 'pay_' + safe_name + ".png")
        try:
            background.save(out_path)
            return out_path
        except Exception as e:
            print("QR image %s could not be saved: %s" % (out_path, e))
        # An unwritable image folder must not stop a payment: the dialog only
        # needs a path that exists.
        out_path = path.join(tempfile.gettempdir(), 'meile_pay_' + safe_name + ".png")
        background.save(out_path)
        return out_path