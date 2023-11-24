import pkg_resources
import qrcode

from PIL import Image
from PIL import ImageDraw, ImageFont
from PIL import ImageOps

from os import path

from conf.meile_config import MeileGuiConfig

from typedef.win import CoinsList

class QRCode():
    IMGDIR = None
    BASEDIR = None
    MeileConfig = None

    def __init__(self):
        self.BASEDIR     = MeileGuiConfig.BASEDIR
        self.IMGDIR      = MeileGuiConfig.IMGDIR
        self.MeileConfig = MeileGuiConfig()

    def generate_qr_code(self, ADDRESS):
        DepositCoin    = CoinsList.coins[2]
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
        w,h  = draw.textsize(DepositAddress)
        draw.text(((QRimg.size[0]+15 - w)/2,QRimg.size[1]-2),DepositAddress, (0,0,0), font=robotoFont)
        
        background.paste(QRimg, (0,0))
        background.save(path.join(self.IMGDIR, DepositCoin + ".png"))
        