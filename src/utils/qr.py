import qrcode

from PIL import Image
from PIL import ImageDraw, ImageFont
from PIL import ImageOps

from os import path
import hashlib
from helpers.helpers import is_ecryptfs_mounted
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
        
    def generate_wg_qr_code(self, conf_path, label=None):

        
        with open(conf_path, 'r') as f:
            wg_config = f.read().strip()
            
        wg_config = wg_config.replace("127.0.0.1,", "")

        if not label:
            label = path.basename(conf_path)

        robotoFont = ImageFont.truetype(self.MeileConfig.resource_path(MeileColors.FONT_FACE), 13)
   
        wg_logo_path = self.MeileConfig.resource_path(
            'utils/coinimg/wireguard.png'
        )
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
        robotoFont = ImageFont.truetype(
            self.MeileConfig.resource_path(MeileColors.QR_FONT_FACE),
            fontSize,
        )

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
        
        coinLogo = self.MeileConfig.resource_path('../utils/coinimg/' + DepositCoin + '.png')
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
        robotoFont = ImageFont.truetype(self.MeileConfig.resource_path('../utils/fonts/Roboto-BoldItalic.ttf'), fontSize)
    
        draw = ImageDraw.Draw(background)
        
        _, _, w, h = draw.textbbox((0, 0), text=str(DepositAddress))
        draw.text(((QRimg.size[0]+15 - w)/2,QRimg.size[1]-2),DepositAddress, (0,0,0), font=robotoFont)
        
        background.paste(QRimg, (0,0))
        
        if ADDRESS.startswith(("vmess", "vless")):
            background.save(path.join(self.IMGDIR, ADDRESS[:5] + ".png"))
            return path.join(self.IMGDIR, ADDRESS[0:5] + ".png")
        elif not is_ecryptfs_mounted() or coin == "dvpn":
            background.save(path.join(self.IMGDIR, ADDRESS + ".png"))
            return path.join(self.IMGDIR, ADDRESS + ".png")
        else:
            hashed_address = hashlib.sha256(ADDRESS.encode()).hexdigest()
            background.save(path.join(self.IMGDIR, hashed_address + ".png"))
            return path.join(self.IMGDIR, hashed_address + ".png")

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

        if coinLogo and path.exists(coinLogo):
            logo = Image.open(coinLogo)
            basewidth = 100
            wpercent = (basewidth / float(logo.size[0]))
            hsize = int((float(logo.size[1]) * float(wpercent)))
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
        robotoFont = ImageFont.truetype(self.MeileConfig.resource_path('../utils/fonts/Roboto-BoldItalic.ttf'), fontSize)

        draw = ImageDraw.Draw(background)
        _, _, w, h = draw.textbbox((0, 0), text=str(ADDRESS), font=robotoFont)
        draw.text(((QRimg.size[0] + 15 - w) / 2, QRimg.size[1] - 2), ADDRESS, (0, 0, 0), font=robotoFont)

        background.paste(QRimg, (0, 0))

        safe_name = ''.join(c if c.isalnum() else '_' for c in ADDRESS)[:120]
        background.save(path.join(self.IMGDIR, 'pay_' + safe_name + ".png"))
        return path.join(self.IMGDIR, 'pay_' + safe_name + ".png")