import pwd
import os
import jwt
import time
import stripe
import pexpect

from flaskext.mysql import MySQL
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth


from werkzeug.security import generate_password_hash, check_password_hash

import scrtxxs

app = Flask(__name__)
mysql = MySQL()
mysql.init_app(app)


stripe.api_key = scrtxxs.StripeSCRTKey

HotWalletAddress = scrtxxs.WalletAddress
keyring_passphrase = scrtxxs.HotWalletPW


DBdir = '/home/' + str(pwd.getpwuid(os.getuid())[0]) + '/dbs'
WalletLogDIR = '/home/' + str(pwd.getpwuid(os.getuid())[0]) + '/Logs'
DBFile = 'sqlite:///' + DBdir + '/dvpn_stripe.sqlite'


# SQLAlchemy Configurations
app.config['SECRET_KEY'] = scrtxxs.SQLAlchemyScrtKey
app.config['SQLALCHEMY_DATABASE_URI'] = DBFile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFCATIONS'] = False

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = scrtxxs.MySQLUsername
app.config['MYSQL_DATABASE_PASSWORD'] = scrtxxs.MySQLPassword
app.config['MYSQL_DATABASE_DB'] = scrtxxs.MySQLDB
app.config['MYSQL_DATABASE_HOST'] = 'localhost'


db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])
 
@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

#@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})

@app.route('/api/users/<int:id>')
def get_user(id): 
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/api/tt', methods=['POST'])
@auth.login_required
def TransferTokens():
    DVPNQtys = [1000, 2000, 5000]
    dvpn_address = request.json.get('address')
    stripe_id    = request.json.get('id')
    dvpn_qty     = request.json.get('qty')
    user_ip      = request.remote_addr
    ExceptionLogFile = open(os.path.join(WalletLogDIR, "exceptions.log"), 'a+')
    StatusDict = {'message' : None}
    TransferLogFile = os.path.join(WalletLogDIR, "dvpn_transfer_status.log")
    
    ofile = open(TransferLogFile, 'a+')
    if int(dvpn_qty) in DVPNQtys:
        if VerifySuccessfulPayment(stripe_id):
            print("Stripe ID: %s" % stripe_id)
            ofile.write("Stripe ID: %s" % stripe_id)
            print("Beginnning Transfer of %sdvpn to %s" % (dvpn_qty,dvpn_address))
            ofile.write("Beginnning Transfer of %sdvpn to %s" % (dvpn_qty,dvpn_address))
            try: 
                if TransferCoinsToPayee(dvpn_address, dvpn_qty):
                    StatusDict['message'] = "%sdvpn transfered from %s to %s" % (dvpn_qty, HotWalletAddress, dvpn_address)
                    ofile.write(StatusDict['message'])
                    ofile.close()
                    UpdateDB(stripe_id, dvpn_address, user_ip, "SUCCESSFUL")
                    return jsonify(StatusDict)
                else:
                    StatusDict['message'] = "Something went wrong. Please contact support@mathnodes.com for more information."
                    UpdateDB(stripe_id, dvpn_address, user_ip, StatusDict['message'])
                    ofile.write(StatusDict['message'])
                    ofile.close()
                    return jsonify(StatusDict)
            except Exception as e:
                ExceptionLogFile.write(str(e) + '\n')
                ExceptionLogFile.close()
                StatusDict['message'] = str(e)
                UpdateDB(stripe_id, dvpn_address, user_ip, StatusDict['message'])
                ofile.write(StatusDict['message'])
                ofile.close()
                return jsonify(StatusDict)
        else:
            StatusDict['message'] = "Payment not marked as paid."
            ofile.write(StatusDict['message'])
            ofile.close()
            UpdateDB(stripe_id, dvpn_address, user_ip, StatusDict['message'])
            return jsonify(StatusDict)
    else:
        StatusDict['message'] = "QTY not supported. Erroneous amount "
        ofile.write(StatusDict['message'])
        ofile.close()
        UpdateDB(stripe_id, dvpn_address, user_ip, StatusDict['message'])
        return jsonify(StatusDict)        
def UpdateDB(stripe_id, dvpn_address, ip, message):
        insquery = '''
                    INSERT IGNORE INTO stripe (stripe_id, receiving_address, ip_address, status, sale_date)
                    VALUES ("%s", "%s", "%s", "%s", NOW());
                    ''' % (stripe_id, dvpn_address, ip, message)
                    
        UpdateStripeTable(insquery)

def UpdateStripeTable(query):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()

def VerifySuccessfulPayment(stripe_id):
    payment_retrieval = stripe.Charge.retrieve(stripe_id,)
    return payment_retrieval['paid']
    
def TransferCoinsToPayee(address,dvpn_qty):
    DVPNBaseAmt = 1000000
    DVPNAmount = str(int(DVPNBaseAmt)*int(dvpn_qty)) + "udvpn"
    WalletLogFile = os.path.join(WalletLogDIR, "dvpn_stripe.log")
    
    
    transfer_cmd = "/home/sentinel/sentinelhub tx bank send --gas auto --gas-prices 0.2udvpn --gas-adjustment 2.0 --yes %s %s %s" % (HotWalletAddress, address, DVPNAmount)
    try: 
        ofile = open(WalletLogFile, 'ab+')
        
        child = pexpect.spawn(transfer_cmd)
        child.logfile = ofile
        
        child.expect("Enter .*")
        child.sendline(keyring_passphrase)
        child.expect(pexpect.EOF)
        
        ofile.flush()
        ofile.close()
    except Exception as e:
        print(str(e))
        return False
    
    return True
    

db.create_all()  
