import pkg_resources
import qrcode

from PIL import Image
from PIL import ImageDraw, ImageFont
from PIL import ImageOps

from os import path

from conf.meile_config import MeileGuiConfig


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
            self.MeileConfig.resource_path(
                'utils/fonts/Roboto-BoldItalic.ttf'
            ),
            fontSize,
        )

        draw = ImageDraw.Draw(background)
        _, _, w, h = draw.textbbox((0, 0), text=str(label))
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
        robotoFont = ImageFont.truetype(self.MeileConfig.resource_path('utils/fonts/Roboto-BoldItalic.ttf'), fontSize)
    
        draw = ImageDraw.Draw(background)
        
        _, _, w, h = draw.textbbox((0, 0), text=str(DepositAddress))
        draw.text(((QRimg.size[0]+15 - w)/2,QRimg.size[1]-2),DepositAddress, (0,0,0), font=robotoFont)
        
        background.paste(QRimg, (0,0))
        if ADDRESS.startswith(("vmess", "vless")):
            background.save(path.join(self.IMGDIR, ADDRESS[:5] + ".png"))
            return path.join(self.IMGDIR, ADDRESS[0:5] + ".png")
        else:
            background.save(path.join(self.IMGDIR, ADDRESS + ".png"))
            return path.join(self.IMGDIR, ADDRESS + ".png")
        