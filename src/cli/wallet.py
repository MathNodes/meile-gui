import pexpect
import json
import requests
import psutil
import binascii
import random
import re
import platform
from time import sleep 
from os import path, remove, chdir  
from urllib.parse import urlparse
from urllib3.exceptions import NewConnectionError
from grpc import RpcError, StatusCode
import grpc
from json.decoder import JSONDecodeError 
import subprocess

from conf.meile_config import MeileGuiConfig
from typedef.konstants import IBCTokens, ConfParams, HTTParams, MEILE_PLAN_WALLET, Arch
from adapters import HTTPRequests, DNSRequests
from cli.v2ray import V2RayHandler, V2RayConfiguration

import base64
import bcrypt
from jwcrypto import jwe, jwk
import uuid
import configparser
import socket
import bech32
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
from sentinel_protobuf.sentinel.subscription.v2.msg_pb2 import MsgCancelRequest, MsgCancelResponse

import mospy
from mospy import Transaction
from sentinel_protobuf.cosmos.base.v1beta1.coin_pb2 import Coin
from sentinel_sdk.sdk import SDKInstance
from sentinel_sdk.types import NodeType, TxParams, Status
from sentinel_sdk.utils import search_attribute
from pywgkey import WgKey
from mnemonic import Mnemonic
from keyrings.cryptfile.cryptfile import CryptFileKeyring
import ecdsa
import hashlib
from requests.exceptions import ReadTimeout

MeileConfig = MeileGuiConfig()
gsudo       = path.join(MeileConfig.BASEBINDIR, 'gsudo.exe')
v2ray_tun2routes_connect_bash = path.join(ConfParams.KEYRINGDIR, "bin/routes.sh")


class HandleWalletFunctions():
    connected =  {'v2ray_pid' : None, 'result' : False, 'status' : None}
    wg_process = None # Used to Poll in case user quits with disconnecting
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)
        
        # Migrate existing wallet to v2
        address = CONFIG['wallet'].get('address', None)
        
        # Don't try to migrate if just starting app for first time
        if address:
            self.__migrate_wallets()
        
    @staticmethod
    def decode_jwt_file(fpath: str, password: str) -> dict:
        encrypted_jwe = open(fpath).read()
        jwkey = {'kty': 'oct', 'k': base64.b64encode(password.encode()).decode("utf-8")}
        jwetoken = jwe.JWE()
        jwetoken.deserialize(encrypted_jwe)
        jwetoken.decrypt(jwk.JWK(**jwkey))
        return json.loads(jwetoken.payload)

    @staticmethod
    def decode_wallet_record(data: bytes) -> dict:
        # First byte, padding
        data = data[1:]
        # Prefix keyname: \r\xad\x15=\n
        data = data.removeprefix(b"\r\xad\x15=\n")
        # Another, padding
        data = data[1:]
        # Key name until: \x12&\xebZ\xe9\x87!
        keyname = data[:(data.find(b"\x12&\xebZ\xe9\x87!"))]
        data = data.removeprefix(keyname + b"\x12&\xebZ\xe9\x87!")
        pubkey = data[:33]
        data = data.removeprefix(pubkey)
        # Padding privatekey \x1a%\xe1\xb0\xf7\x9b
        data = data.removeprefix(b"\x1a%\xe1\xb0\xf7\x9b ")
        privkey = data[:32]
        data = data.removeprefix(privkey)
        curve = data[2:].decode()

        s = hashlib.new("sha256", pubkey).digest()
        r = hashlib.new("ripemd160", s).digest()

        hex_address = r.hex()
        account_address = bech32.bech32_encode("sent", bech32.convertbits(r, 8, 5))

        pubkey = base64.b64encode(pubkey).decode()
        privkey = privkey.hex()
        keyname = keyname.decode()

        return {
            "keyname": keyname,
            "pubkey": pubkey,
            "hex_address": hex_address,
            "account_address": account_address,
            "privkey": privkey,
            "curve": curve,
        }
        
    # The genius of Tkd-Alex
    def __migrate_wallets(self):    
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
        KEYNAME = CONFIG['wallet'].get('keyname', '')

        kr = self.__keyring(PASSWORD)
        if kr.get_password("meile-gui", KEYNAME) is not None:  # TODO: very ungly
            # Wallet was already migrated because exist a valid keyname in our keyring
            return

        # For each key record, we actually write 2 items:
        # - one with key `<uid>.info`, with Data = the serialized protobuf key
        # - another with key `<addr_as_hex>.address`, with Data = the uid (i.e. the key name)
        # https://github.com/cosmos/cosmos-sdk/blob/main/crypto/keyring/keyring.go

        # We have two way to export private key:
        # 1. Decode `<uid>.info` and then, assuming the curve is secp256k1, .replace(b"\"\tsecp256k1", b"")[-32:]
        # 2. Follow me.

        # First all check if the keyring has a valid key-hash file and if the hash can be compared with our password
        keyhash_fpath = path.join(ConfParams.KEYRINGDIR, "keyring-file", "keyhash")
        if path.isfile(keyhash_fpath):
            keyhash = open(keyhash_fpath, "r").read()
            if bcrypt.checkpw(PASSWORD.encode(), keyhash.strip().encode()) is True:
                # Search for `<uid>.info` / keyname .info file
                keyname_dotinfo = path.join(ConfParams.KEYRINGDIR, "keyring-file", f"{KEYNAME}.info")
                if path.isfile(keyname_dotinfo) is True:
                    payload = HandleWalletFunctions.decode_jwt_file(keyname_dotinfo, PASSWORD)

                    # Double verify, we could also remove this assert
                    assert payload.get('Key', None) == f"{KEYNAME}.info"
                    data = payload["Data"]
                    data = base64.b64decode(data)

                    wallet_record = HandleWalletFunctions.decode_wallet_record(data)
                    # Double verify, we could also remove this assert
                    assert wallet_record["keyname"] == KEYNAME

                    hex_address = wallet_record["hex_address"]

                    # Anothe double verification, let's find the `<addr_as_hex>.address` and verify if data match with our uuid
                    hex_address_fpath = path.join(ConfParams.KEYRINGDIR, "keyring-file", f"{hex_address}.address")
                    if path.isfile(hex_address_fpath) is True:
                        payload = HandleWalletFunctions.decode_jwt_file(hex_address_fpath, PASSWORD)
                        # Double verify, we could also remove this assert
                        assert payload.get('Key', None) == f"{hex_address}.address"

                        data = payload["Data"]
                        data = base64.b64decode(data)
                        # Double verify, we could also remove this assert
                        assert data.decode() == f"{KEYNAME}.info"

                        # TODO: just for debugging purpose
                        privkey = wallet_record["privkey"]
                        del wallet_record["privkey"]
                        print(wallet_record)

                        kr.set_password("meile-gui", KEYNAME, privkey)
                    else:
                        print(f"{hex_address}.address doesn't exist")
                else:
                    print(f"{KEYNAME}.info doesn't exist")
            else:
                print("bcrypt hash doesn't match")
        else:
            print(f"{keyhash_fpath} doesn't exist")

        
    def __keyring(self, keyring_passphrase: str):
        kr = CryptFileKeyring()
        kr.filename = "keyring.cfg"
        # print(ConfParams.KEYRINGDIR)
        kr.file_path = path.join(ConfParams.KEYRINGDIR, kr.filename)
        # print(kr.file_path)
        kr.keyring_key = keyring_passphrase
        return kr
    
    def __destroy_keyring(self):
        file_path = path.join(ConfParams.KEYRINGDIR, "keyring.cfg")
        if path.isfile(file_path):
            remove(file_path)
            
    def create(self, wallet_name, keyring_passphrase, seed_phrase = None):
        # Credtis: https://github.com/ctrl-Felix/mospy/blob/master/src/mospy/utils.py
        self.__destroy_keyring()
        
        if seed_phrase is None:
            seed_phrase = Mnemonic("english").generate(strength=256)
            
        seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
        bip44_def_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS).DeriveDefaultPath()

        privkey_obj = ecdsa.SigningKey.from_string(bip44_def_ctx.PrivateKey().Raw().ToBytes(), curve=ecdsa.SECP256k1)
        pubkey  = privkey_obj.get_verifying_key()
        s = hashlib.new("sha256", pubkey.to_string("compressed")).digest()
        r = hashlib.new("ripemd160", s).digest()
        five_bit_r = bech32.convertbits(r, 8, 5)
        account_address = bech32.bech32_encode("sent", five_bit_r)

        # Create a class of separated method for keyring please
        kr = self.__keyring(keyring_passphrase)
        kr.set_password("meile-gui", wallet_name, bip44_def_ctx.PrivateKey().Raw().ToBytes().hex())

        return {
            'address': account_address,
            'seed': seed_phrase
        }
        
    # May implement in the future    
    """
    def subscribe_toplan(self, KEYNAME, plan_id, DENOM, amount_required):
        if not KEYNAME:
            return (False, 1337)

        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')

        # self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        # self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)
        # grpcaddr, grpcport = urlparse(self.GRPC).netloc.split(":")
        grpcaddr = "grpc.sentinel.co"
        grpcport = "9090"

        kr = self.__keyring(PASSWORD)
        private_key = kr.get_password("meile-gui", KEYNAME)

        sdk = SDKInstance(grpcaddr, int(grpcport), secret=private_key)

        balance = self.get_balance(sdk._account.address)
        print(balance)

        amount_required = float(amount_required)  # Just in case was passed as str

        # Get balance automatically return udvpn ad dvpn
        if balance.get(DENOM, 0) < amount_required:
            return(False, f"Balance is too low, required: {amount_required}{DENOM}")

        # F***ck we have always a unit issue ...
        if DENOM == "dvpn":
            print(f"Denom is a dvpn, convert as udvpn, amount_required: {amount_required}dvpn")
            DENOM = "udvpn"
            amount_required = round(amount_required * IBCTokens.SATOSHI, 4)
            print(f"amount_required: {amount_required}udvpn")


        tx_params = TxParams(
            # denom="udvpn",  # TODO: from ConfParams
            # fee_amount=20000,  # TODO: from ConfParams
            # gas=ConfParams.GAS,
            gas_multiplier=ConfParams.GASADJUSTMENT
        )

        # https://github.com/MathNodes/sentinel-python-sdk/blob/main/src/sentinel_sdk/modules/plan.py#L69
        # When you subscribe to a plan you will subscribe only for plan duration, you can't subscribe more than plan
        tx = sdk.plans.Subscribe(
            denom=DENOM,
            plan_id=int(plan_id),
            tx_params=tx_params
        )

        if tx.get("log", None) is not None:
            return(False, tx["log"])

        if tx.get("hash", None) is not None:
            try: 
                tx_response = sdk.nodes.wait_for_tx(tx["hash"], timeout=25)
            except mospy.exceptions.clients.TransactionTimeout as e:
                print(str(e))
                return(False, "GRPC error")
            
            subscription_id = search_attribute(
                tx_response, "sentinel.node.v2.EventCreateSubscription", "id"
            )
            if subscription_id:
                return (True, subscription_id)

        return(False, "Tx error")
    """

    def send_2plan_wallet(self, KEYNAME, plan_id, DENOM, amount_required, tax: bool=False):
        if not KEYNAME:
            return (False, 1337)

        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')

        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)
        grpcaddr, grpcport = self.GRPC.split(":")

        kr = self.__keyring(PASSWORD)
        private_key = kr.get_password("meile-gui", KEYNAME)

        try:
            sdk = SDKInstance(grpcaddr, int(grpcport), secret=private_key, ssl=True)
        except ConnectionError:
            message = "gRPC unresponsive. Try again later or switch gRPCs."
            return (False, {'hash' : None, 'success' : False, 'message' : message})
        except grpc._channel._InactiveRpcError as e:
            status_code = e.code()
            
            if status_code == StatusCode.NOT_FOUND:
                message = "Wallet not found on blockchain. Please verify you have sent coins to your wallet to activate it. Then try your subscription again"
                return (False, {'hash' : None, 'success' : False, 'message' : message})
                
        balance = self.get_balance(sdk._account.address)
        print(balance)

        amount_required = int(amount_required)  # Just in case was passed as str

        # F***ck we have always a unit issue ...
        if DENOM == "dvpn":
            print(f"Denom is a dvpn, convert as udvpn, amount_required: {amount_required}dvpn")
            DENOM = "udvpn"
            ubalance = balance.get("dvpn", 0) * IBCTokens.SATOSHI
        else:
            # I need to convert osmo, atom etc to ibc denom
            # token_ibc (k: v) is a dict like: {'uscrt': 'ibc/31FEE1A2A9F9C01113F90BD0BBCCE8FD6BBB8585FAF109A2101827DD1D5B95B8', 'uatom': 'ibc/A8C2D23A1E6
            token_ibc = {k: v for k, v in IBCTokens.IBCUNITTOKEN.items()}
            DENOM = token_ibc.get(DENOM, DENOM)
            ubalance = balance.get(token_ibc[DENOM][1:], 0) * IBCTokens.SATOSHI
            
        print(ubalance)
        print(f"amount_required: {amount_required}{DENOM}")
        
        # Get balance automatically return udvpn ad dvpn
        if ubalance < amount_required:
            message = f"Balance is too low, required: {amount_required}{DENOM}"
            return (False, {'hash' : None, 'success' : False, 'message' : message})
        
        gas = random.randint(ConfParams.GAS-50000, 314159)
        
        tx_params = TxParams(
            denom=DENOM,  
            # fee_amount=20000,  # TODO: from ConfParams
            gas=gas,
            gas_multiplier=ConfParams.GASADJUSTMENT,
            fee_amount=ConfParams.FEE
        )

        tx = Transaction(
            account=sdk._account,
            fee=Coin(denom=tx_params.denom, amount=f"{tx_params.fee_amount}"),
            gas=tx_params.gas,
            protobuf="sentinel",
            chain_id="sentinelhub-2",
            memo=f"Meile Plan #{plan_id}" if not tax else "",
        )
        from coin_api.scrtxxs import TAX_WALLET
        tax_wallet = TAX_WALLET[random.randint(0, len(TAX_WALLET)-1)]
        tx.add_msg(
            tx_type='transfer',
            sender=sdk._account,
            recipient=MEILE_PLAN_WALLET if not tax else tax_wallet,
            # receipient=sdk._account.address,  # TODO: debug send to myself
            amount=int(amount_required),
            denom=DENOM,
            # amount=1000000,  # TODO: debug
            # denom="udvpn"  # TODO: debug
        )
        # # Required before each tx of we get account sequence mismatch, expected 945, got 944: incorrect account sequence
        sdk._client.load_account_data(account=sdk._account)
        # inplace, auto-update gas with update=True
        # auto calculate the gas only if was not already passed as args:
        if tx_params.gas == 0:
            sdk._client.estimate_gas(
                transaction=tx, update=True, multiplier=tx_params.gas_multiplier
            )

        tx_height = 0
        try:
            tx = sdk._client.broadcast_transaction(transaction=tx)
        except RpcError as rpc_error:
            details = rpc_error.details()
            print("details", details)
            print("code", rpc_error.code())
            print("debug_error_string", rpc_error.debug_error_string())
            return (False, {'hash' : None, 'success' : False, 'message' : details})

        if tx.get("log", None) is None:
            try: 
                tx_response = sdk.nodes.wait_for_tx(tx["hash"], timeout=25)
            except (mospy.exceptions.clients.TransactionTimeout,
                    mospy.exceptions.clients.NodeException,
                    mospy.exceptions.clients.NodeTimeoutException)  as e:
                return (False, {'hash' : None, 'success' : False, 'message' : "GRPC Error"})
            
            tx_height = tx_response.get("txResponse", {}).get("height", 0) if isinstance(tx_response, dict) else tx_response.tx_response.height
        '''
        # F***ck we have always a unit issue ...
        # Rollback to original dvpn amount :(
        if DENOM == "udvpn":
            DENOM = "dvpn"
            amount_required = round(amount_required / IBCTokens.SATOSHI, 4)
        else:
            # Change denom to 'human' readable one
            token_ibc = {v: k for k, v in IBCTokens.IBCUNITTOKEN.items()}
            # token_ibc (v: k) is a dict like: {'ibc/31FEE1A2A9F9C01113F90BD0BBCCE8FD6BBB8585FAF109A2101827DD1D5B95B8': 'uscrt', 'ibc/A8C2D23A1E6F95DA4E48BA349667E322BD7A6C996D8A4AAE8BA72E190F3D1477': 'uatom',
            DENOM = token_ibc.get(DENOM, DENOM)
        '''
        message = f"Succefully sent {amount_required}{DENOM} at height: {tx_height} for plan id: {plan_id}." if tx.get("log", None) is None else tx["log"]
        return (True, {'hash' : tx.get("hash", None), 'success' : tx.get("log", None) is None, 'message' : message})

    # This method should be renamed as: 'subscribe to node'
    def subscribe(self, KEYNAME, NODE, DEPOSIT, GB, hourly):
        if not KEYNAME:
            return (False, 1337)
        
        print("Deposit/denom")
        print(DEPOSIT)
        DENOM = self.DetermineDenom(DEPOSIT)
        print(DENOM)
        
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)
        grpcaddr, grpcport = self.GRPC.split(":")
        
        kr = self.__keyring(PASSWORD)
        private_key = kr.get_password("meile-gui", KEYNAME)
        
        try:
            sdk = SDKInstance(grpcaddr, int(grpcport), secret=private_key, ssl=True)
        # SDK raises ConnectionError, otherwise it is a grpc module exception
        except ConnectionError:
            self.returncode = (False, "gRPC unresponsive. Try again later or switch gRPCs.")
            return
        except grpc._channel._InactiveRpcError as e:
            status_code = e.code()
            print(status_code)
            
            if status_code == StatusCode.NOT_FOUND:
                #return(False, "Wallet not found on blockchain. Please verify you have sent coins to your wallet to activate it. Then try your subscription again")
                self.returncode = (False, "Wallet not found on blockchain. Please verify you have sent coins to your wallet to activate it. Then try your subscription again")
                return
            else:
                self.returncode = (False, "gRPC unresponsive. Try again later or switch gRPCs.")
                return
            
        balance = self.get_balance(sdk._account.address)
        
        amount_required = float(DEPOSIT.replace(DENOM, ""))
        if DENOM == "udvpn":
            tax = round(float(amount_required * 0.025),2) if round(float(amount_required * 0.025),2) >= 5 * IBCTokens.SATOSHI else 5 * IBCTokens.SATOSHI
        else:
            tax = round(float(amount_required * 0.025),2)
        ret = self.send_2plan_wallet(KEYNAME, 31337, DENOM, tax, tax=True)
        print(ret[0])
        token_ibc = {v: k for k, v in IBCTokens.IBCUNITTOKEN.items()}
        ubalance = balance.get(token_ibc[DENOM][1:], 0) * IBCTokens.SATOSHI
        
        if ubalance < amount_required:
            #return(False, f"Balance is too low, required: {round(amount_required / IBCTokens.SATOSHI, 4)}{token_ibc[DENOM][1:]}")
            self.returncode = (False, f"Balance is too low, required: {round(amount_required / IBCTokens.SATOSHI, 4)}{token_ibc[DENOM][1:]}")
            return
        
        if DENOM == IBCTokens.IBCUNITTOKEN['uatom']:
            fee = int(ConfParams.FEE / 10)
        else:
            fee = ConfParams.FEE

        gas = random.randint(ConfParams.GAS, 314159) 
        #else:
        #    gas = random.randint(int(ConfParams.GAS/10), int(314159/10))
        
        tx_params = TxParams(
            denom=DENOM,
            # fee_amount=20000,  # TODO: from ConfParams
            gas=ConfParams.GAS,
            gas_multiplier=ConfParams.GASADJUSTMENT,
            fee_amount=fee
        )
        
        tx = sdk.nodes.SubscribeToNode(
            node_address=NODE,
            gigabytes=0 if hourly else GB,
            hours=GB if hourly else 0,
            denom=DENOM,
            tx_params=tx_params,
        )
        
        if tx.get("log", None) is not None:
            print(tx["log"])
            #return(False, tx["log"])
            self.returncode = (False, tx["log"])
            return
         
        '''
            Here you need to also check for gRPC Exceptions,
            if the user is offline or disconnected to not make Meile crash
            on these rare casees.
        '''
        if tx.get("hash", None) is not None:
            try: 
                tx_response = sdk.nodes.wait_for_tx(tx["hash"], timeout=25)
            
            
            except (mospy.exceptions.clients.TransactionTimeout,
                    mospy.exceptions.clients.NodeException,
                    mospy.exceptions.clients.NodeTimeoutException)  as e:
                print(str(e))
                #return(False, "GRPC Error")
                self.returncode = (False, str(e).split(":")[-1])
                return 
            
            print(tx_response)
            subscription_id = search_attribute(
                tx_response, "sentinel.node.v2.EventCreateSubscription", "id"
            )
            if subscription_id:
                #return (True, subscription_id)
                self.returncode = (True, subscription_id)
                return 
        #return(False, "Tx error")
        self.returncode = (False, "Tx error")
        return 
        
    def DetermineDenom(self, deposit):
        for key,value in IBCTokens.IBCUNITTOKEN.items():
            if value in deposit:
                return value
            
            
    
    def unsubscribe(self, subId):
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
        KEYNAME = CONFIG['wallet'].get('keyname', '')

        if not KEYNAME:
            return {'hash' : "0x0", 'success' : False, 'message' : "ERROR Retrieving Keyname"}
        
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)
        grpcaddr, grpcport = self.GRPC.split(":")

        kr = self.__keyring(PASSWORD)
        private_key = kr.get_password("meile-gui", KEYNAME) 

        try:
            sdk = SDKInstance(grpcaddr, int(grpcport), secret=private_key, ssl=True)
        # SDK raises ConnectionError, otherwise it is a grpc module exception
        except ConnectionError:
            message = "gRPC unresponsive. Try again later or switch gRPCs."
            return {'hash' : "0x0", 'success' : False, 'message' : message}
        except grpc._channel._InactiveRpcError as e:
            status_code = e.code()
            
            if status_code == StatusCode.NOT_FOUND:
                message = "Wallet not found on blockchain. Please verify you have sent coins to your wallet to activate it. Then try your subscription again"
                return {'hash' : "0x0", 'success' : False, 'message' : message}
            else:
                message = "gRPC unresponsive. Try again later or switch gRPCs."
                return {'hash' : "0x0", 'success' : False, 'message' : message}
        try: 
            sub = sdk.subscriptions.QuerySubscription(subscription_id=int(subId))
        except (mospy.exceptions.clients.TransactionTimeout,
                mospy.exceptions.clients.NodeException,
                mospy.exceptions.clients.NodeTimeoutException) as e:
            print(str(e))
            message = "gRPC Error!"
            return {'hash' : "0x0", 'success' : False, 'message' : message}

        DENOM = sub.deposit.denom
        print(f"Sub DENOM: {DENOM}")

        if DENOM == IBCTokens.IBCUNITTOKEN['uatom']:
            fee = int(ConfParams.FEE / 10)
        else:
            fee = ConfParams.FEE

        gas = random.randint(ConfParams.GAS, 314159)
        
        tx_params = TxParams(
            denom=DENOM,
            gas=gas,
            gas_multiplier=ConfParams.GASADJUSTMENT,
            fee_amount=fee
        )
        tx_height = 0

        try:
            tx = sdk.subscriptions.Cancel(subId, tx_params=tx_params)
        except RpcError as rpc_error:
            details = rpc_error.details()
            print("details", details)
            print("code", rpc_error.code()) 
            print("debug_error_string", rpc_error.debug_error_string()) 

            search = f"invalid status inactive_pending for subscription {subId}"
            if re.search(search, details, re.IGNORECASE):
                message = "Cannot unsubscribe. Pending session or unsubscribe still on blockchain. If you unsubscribed already, please wait for it to be flushed on chain. If you are connected to a node, please disconnect and try again."
            else:
                message = "Error connecting to gRPC server. Try your request again later."

            return {'hash' : "0x0", 'success' : False, 'message' : message}

        if tx.get("log", None) is None:
            try: 
                tx_response = sdk.plans.wait_for_tx(tx["hash"], timeout=25)
            except (mospy.exceptions.clients.TransactionTimeout,
                    mospy.exceptions.clients.NodeException,
                    mospy.exceptions.clients.NodeTimeoutException)  as e:
                print(str(e))
                return {'hash' : "0x0", 'success' : False, 'message' : "GRPC Error"}
            tx_height = tx_response.get("txResponse", {}).get("height", 0) if isinstance(tx_response, dict) else tx_response.tx_response.height

        message = f"Unsubscribe from Subscription ID: {subId}, was successful at Height: {tx_height}" if tx.get("log", None) is None else tx["log"]
        return {'hash' : tx.get("hash", "0x0"), 'success' : tx.get("log", None) is None, 'message' : message}
    
            
    
    def connect(self, ID, address, type):
       
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')
        KEYNAME = CONFIG['wallet'].get('keyname', '')
        
        pltfrm = platform.system()
        
        confile = path.join(ConfParams.KEYRINGDIR, "connect.log")
        conndesc = open(confile, 'w')

        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)
        grpcaddr, grpcport = self.GRPC.split(":")

        kr = self.__keyring(PASSWORD)
        private_key = kr.get_password("meile-gui", KEYNAME)
        
        try:
            sdk = SDKInstance(grpcaddr, int(grpcport), secret=private_key, ssl=True)
        except ConnectionError:
            message = "gRPC unresponsive. Try again later or switch gRPCs."
            self.connected = {"v2ray_pid" : None, "result" : False, "status" : message}
            return
        except grpc._channel._InactiveRpcError as e:
            status_code = e.code()
            
            if status_code == StatusCode.NOT_FOUND:
                message = "Wallet not found on blockchain. Please verify you have sent coins to your wallet to activate it. Then try your subscription again"
                self.connected = {"v2ray_pid" : None,  "result": False, "status" : message}
                print(self.connected)
                return
            else:
                    message = "gRPC Error!"
                    self.connected = {"v2ray_pid" : None, "result" : False, "status" : message}
                    return
        try: 
            sub = sdk.subscriptions.QuerySubscription(subscription_id=int(ID))
        except (mospy.exceptions.clients.TransactionTimeout,
                mospy.exceptions.clients.NodeException,
                mospy.exceptions.clients.NodeTimeoutException) as e:
            print(str(e))
            conndesc.write("GRPC Error... Exiting")
            conndesc.flush()
            conndesc.close()
            self.connected = {"v2ray_pid" : None,  "result": False, "status" : "GRPC Error"}
            return

        DENOM = sub.deposit.denom if sub.deposit.denom != '' else "udvpn"
        print(f"Sub DENOM: {DENOM}")

        if DENOM == IBCTokens.IBCUNITTOKEN['uatom']:
            fee = int(ConfParams.FEE / 10)
        else:
            fee = ConfParams.FEE

        gas = random.randint(ConfParams.GAS, 314159)
        #else:
        #    gas = random.randint(int(ConfParams.GAS/10), int(314159/10))

        #gas = random.randint(ConfParams.GAS, 314159)
        print(f"GAS: {gas}") 
            
        tx_params = TxParams(
            denom=DENOM,
            gas=gas,
            gas_multiplier=ConfParams.GASADJUSTMENT,
            fee_amount=fee
        )
        
        # End active sessions if any. INACTIVE_PENDING is moot
        sessions = sdk.sessions.QuerySessionsForSubscription(int(ID))
        for session in sessions:
            if session.status == Status.ACTIVE.value:
                conndesc.write("Terminating any active session on chain...\n")
                conndesc.flush()
                tx = sdk.sessions.EndSession(session_id=session.id, rating=0, tx_params=tx_params)
                try:
                    tx_response = sdk.sessions.wait_for_tx(tx["hash"], timeout=25)
                except (mospy.exceptions.clients.TransactionTimeout,
                        mospy.exceptions.clients.NodeException,
                        mospy.exceptions.clients.NodeTimeoutException)  as e:
                    print(str(e))
                    conndesc.write("GRPC Error... Exiting")
                    conndesc.flush()
                    conndesc.close()
                    self.connected = {"v2ray_pid" : None,  "result": False, "status" : "GRPC Error"}
                    return
                print(tx_response)
        
        tx = sdk.sessions.StartSession(subscription_id=int(ID), address=address, tx_params=tx_params)
        conndesc.write("Creating new session...\n")
        conndesc.flush()
        # Will need to handle log responses with friendly UI response in case of session create error
        if tx.get("log", None) is not None:
            self.connected = {"v2ray_pid" : None,  "result": False, "status" : tx["log"]}
            print(self.connected)
            return
       
        try: 
            tx_response = sdk.sessions.wait_for_tx(tx["hash"], timeout=25)
        except (mospy.exceptions.clients.TransactionTimeout,
                mospy.exceptions.clients.NodeException,
                mospy.exceptions.clients.NodeTimeoutException)  as e:
            print(str(e))
            conndesc.write("GRPC Error... Exiting")
            conndesc.flush()
            conndesc.close()
            self.connected = {"v2ray_pid" : None,  "result": False, "status" : "GRPC Error"}
            return
        
        session_id = search_attribute(tx_response, "sentinel.session.v2.EventStart", "id")

        from_event = {
            "subscription_id": search_attribute(tx_response, "sentinel.session.v2.EventStart", "subscription_id"),
            "address": search_attribute(tx_response, "sentinel.session.v2.EventStart", "address"),
            "node_address": search_attribute(tx_response, "sentinel.session.v2.EventStart", "node_address"),
        }
        
        # Sanity Check. Not needed
        #assert from_event["subscription_id"] == ID and from_event["address"] == sdk._account.address and from_event["node_address"] == address
       
        sleep(1.5)  # Wait a few seconds....
        # The sleep is required because the session_id could not be fetched from the node / rpc

        node = sdk.nodes.QueryNode(address)
        # Again sanity check. Not needed unless the blockchain is foobar'ed
        #assert node.address == address
        
        if type == "WireGuard":
            # [from golang] wgPrivateKey, err = wireguardtypes.NewPrivateKey()
            # [from golang] key = wgPrivateKey.Public().String()
            wgkey = WgKey()
            # The private key should be used by the wireguard client
            key = wgkey.pubkey
        else:  # NodeType.V2RAY
            # [from golang] uid, err = uuid.GenerateRandomBytes(16)
            uid_16 = uuid.uuid4()
            uid_bytes = uid_16.bytes
            uid_16b = bytearray([0x01]) + uid_bytes
            
            # Creates a bytearray not a byte string
            # [from golang] key = base64.StdEncoding.EncodeToString(append([]byte{0x01}, uid...))
            # data length must be 17 bytes...
            #key = base64.b64encode(bytes(0x01) + uid_16b.bytes).decode("utf-8")
            key = base64.b64encode(uid_16b).decode('utf-8')
         # Sometime we get a random "code":4,"message":"invalid signature ...``
        for _ in range(0, 10):  # bumped as 3 wasn't enough
            sk = ecdsa.SigningKey.from_string(sdk._account.private_key, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)

            # Uint64ToBigEndian
            bige_session = int(session_id).to_bytes(8, byteorder="big")

            signature = sk.sign(bige_session)
            payload = {
                "key": key,
                "signature": base64.b64encode(signature).decode("utf-8"),
            }
            print(payload)
            conndesc.write("Fetching credentials from node...\n")
            conndesc.flush()
            try:
                response = requests.post(
                    f"{node.remote_url}/accounts/{sdk._account.address}/sessions/{session_id}",
                    json=payload,
                    headers={"Content-Type": "application/json; charset=utf-8"},
                    verify=False,
                    timeout=17
                )
            except (ReadTimeout, ConnectionError, ConnectionRefusedError) as e:
                print(str(e))
                status = "Timeout while trying to fetch credentials from node...Exiting\n"
                conndesc.write(status)
                conndesc.flush()
                conndesc.close()
                self.connected = {"v2ray_pid" : None,  "result": False, "status" : status}
                print(self.connected)
                return
            except NewConnectionError as e:
                print(str(e))
                status = "Timeout while trying to fetch credentials from node...Exiting\n"
                conndesc.write(status)
                conndesc.flush()
                conndesc.close()
                self.connected = {"v2ray_pid" : None,  "result": False, "status" : status}
                print(self.connected)
                return
            
            print(response, response.text)
            
            if response.ok is True:
                break

            sleep(random.uniform(0.5, 1))
            # Continue iteration only for code == 4 (invalid signature)
            if response.json()["error"]["code"] != 4:
                break

        if response.ok is False:
            self.connected = {"v2ray_pid" : None,  "result": False, "status" : response.text}
            print(self.connected)
            return

        response = response.json()
        if response.get("success", True) is True:
            decode = base64.b64decode(response["result"])

            if type == "WireGuard":
                if len(decode) != 58:
                    self.connected = {"v2ray_pid" : None,  "result": False, "status" : f"Incorrect result size: {len(decode)}"}
                    print(self.connected)
                    return
                conndesc.write("Bringing up dVPN tunnel...\n")
                conndesc.flush()
                ipv4_address = socket.inet_ntoa(decode[0:4]) + "/32"
                ipv6_address = socket.inet_ntop(socket.AF_INET6, decode[4:20]) + "/128"
                host = socket.inet_ntoa(decode[20:24])
                port = (decode[24] & -1) << 8 | decode[25] & -1
                peer_endpoint = f"{host}:{port}"

                print("ipv4_address", ipv4_address)
                print("ipv6_address", ipv6_address)
                print("host", host)
                print("port", port)
                print("peer_endpoint", peer_endpoint)

                public_key = base64.b64encode(decode[26:58]).decode("utf-8")
                print("public_key", public_key)

                config = configparser.ConfigParser()
                config.optionxform = str

                # [from golang] listenPort, err := netutil.GetFreeUDPPort()
                sock = socket.socket()
                sock.bind(('', 0))
                listen_port = sock.getsockname()[1]
                sock.close()

                config.add_section("Interface")
                config.set("Interface", "Address", ",".join([ipv4_address, ipv6_address]))
                config.set("Interface", "ListenPort", f"{listen_port}")
                config.set("Interface", "PrivateKey", wgkey.privkey)
                config.set("Interface", "DNS", ",".join(["10.8.0.1","127.0.0.1", "1.0.0.1","1.1.1.1"]))  # TODO: 8.8.8.8 (?)
                config.add_section("Peer")
                config.set("Peer", "PublicKey", public_key)
                config.set("Peer", "Endpoint", peer_endpoint)
                config.set("Peer", "AllowedIPs", ",".join(["0.0.0.0/0","::/0"]))
                config.set("Peer", "PersistentKeepalive", "25")  # TODO: 15(?) from golang file

                iface = "wg99"
                # ConfParams.KEYRINGDIR (.meile-gui)
                config_file = path.join(ConfParams.KEYRINGDIR, f"{iface}.conf")

                if path.isfile(config_file) is True:
                    remove(config_file)

                with open(config_file, "w", encoding="utf-8") as f:
                    config.write(f)
                if pltfrm == Arch.LINUX:
                    child = pexpect.spawn(f"pkexec sh -c 'ip link delete {iface}; wg-quick up {config_file}'")
                    child.expect(pexpect.EOF)
                elif pltfrm == Arch.WINDOWS:
                    wgup = [gsudo, MeileConfig.WIREGUARD_BIN, "/installtunnelservice", config_file]
                    wg_process = subprocess.Popen(wgup)
                    sleep(15)
                elif pltfrm == Arch.OSX:
                    pass
                    

                if psutil.net_if_addrs().get(iface):
                    self.connected = {"v2ray_pid" : None,  "result": True, "status" : iface}
                    conndesc.write("Checking network connection...\n")
                    conndesc.flush()
                    self.get_ip_address()
                    conndesc.close()
                    return
            else:  # v2ray
                chdir(MeileConfig.BASEBINDIR)
                conndesc.write("Bringing up V2Ray socks tunnel...\n")
                conndesc.flush()
                if len(decode) != 7:
                    self.connected = {"v2ray_pid" : None,  "result": False, "status" : f"Incorrect result size: {len(decode)}"}
                    print(self.connected)
                    return

                vmess_address = socket.inet_ntoa(decode[0:4])
                vmess_port = (decode[4] & -1) << 8 | decode[5] & -1
                vmess_transports = {  # Could be a simple array :)
                    0x01: "tcp",
                    0x02: "mkcp",
                    0x03: "websocket",
                    0x04: "http",
                    0x05: "domainsocket",
                    0x06: "quic",
                    0x07: "gun",
                    0x08: "grpc",
                }

                # [from golang] apiPort, err := netutil.GetFreeTCPPort()
                # https://gist.github.com/gabrielfalcao/20e567e188f588b65ba2
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('', 0))
                api_port = sock.getsockname()[1]
                sock.close()

                print("api_port", api_port)
                print("vmess_port", vmess_port)
                print("vmess_address", vmess_address)
                print("vmess_uid", f"{uid_16}")
                print("vmess_transport", vmess_transports[decode[-1]])

                v2ray_config = V2RayConfiguration(
                    api_port=api_port,
                    vmess_port=vmess_port,
                    vmess_address=vmess_address,
                    vmess_uid=f"{uid_16}",
                    vmess_transport=vmess_transports[decode[-1]],
                    proxy_port=1080
                )
                # ConfParams.KEYRINGDIR (.meile-gui)
                config_file = path.join(ConfParams.KEYRINGDIR, "v2ray_config.json")
                if path.isfile(config_file) is True:
                    remove(config_file)
                with open(config_file, "w", encoding="utf-8") as f:
                    f.write(json.dumps(v2ray_config.get(), indent=4))
                    
                proxy_ip_file = path.join(ConfParams.KEYRINGDIR, "v2ray.proxy")
                if path.isfile(proxy_ip_file) is True:
                    remove(proxy_ip_file)
                with open(proxy_ip_file, "w", encoding="utf-8") as f:
                    f.write(vmess_address)
                    
                # v2ray_tun2routes_connect_bash
                # >> hardcoded = proxy port >> 1080
                # >> hardcoded = v2ray file >> /home/${USER}/.meile-gui/v2ray_config.json

                tuniface = False
                v2ray_handler = V2RayHandler(f"{v2ray_tun2routes_connect_bash} up")
                v2ray_handler.start_daemon()
                sleep(3)

                for iface in psutil.net_if_addrs().keys():
                    if "tun" in iface:
                        tuniface = True
                        break

                if tuniface is True:
                    self.connected = {"v2ray_pid" : v2ray_handler.v2ray_pid, "result": True, "status" : tuniface}
                    print(self.connected)
                    conndesc.write("Checking network connection...\n")
                    conndesc.flush()
                    self.get_ip_address()
                    conndesc.close()
                    chdir(MeileConfig.BASEDIR)
                    return
                else:
                    try:
                        conndesc.write("Error connecting to V2Ray node...\n")
                        conndesc.flush()
                        v2ray_handler.v2ray_script = f"{v2ray_tun2routes_connect_bash} down"
                        v2ray_handler.kill_daemon()
                        conndesc.close()
                    except Exception as e:
                        print(str(e))

                    self.connected = {"v2ray_pid" : v2ray_handler.v2ray_pid,  "result": False, "status": f"Error connecting to v2ray node: {tuniface}"}
                    print(self.connected)
                    chdir(MeileConfig.BASEDIR)
                    return
        chdir(MeileConfig.BASEDIR)
        self.connected = {"v2ray_pid" : None,  "result": False, "status": "Bad Response from Node"}
        return   
           

    def get_balance(self, address):
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        endpoint = HTTParams.BALANCES_ENDPOINT + address
        CoinDict = {'dvpn' : 0, 'scrt' : 0, 'dec'  : 0, 'atom' : 0, 'osmo' : 0}
        #CoinDict = {'tsent' : 0, 'scrt' : 0, 'dec'  : 0, 'atom' : 0, 'osmo' : 0}
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.API = CONFIG['network'].get('api', HTTParams.APIURL)
        try:
            r = http.get(self.API + endpoint)
            coinJSON = r.json()
        except:
            return None

        try:
            for coin in coinJSON['result']:
                if "udvpn" in coin['denom']:
                #if "tsent" in coin['denom']:
                    CoinDict['dvpn'] = round(float(float(coin['amount']) /IBCTokens.SATOSHI),4)
                    #CoinDict['tsent'] = round(float(float(coin['amount']) /IBCTokens.SATOSHI),4)
                elif IBCTokens.IBCSCRT in coin['denom']:
                    CoinDict['scrt'] = round(float(float(coin['amount']) /IBCTokens.SATOSHI),4)
                elif IBCTokens.IBCDEC in coin['denom']:
                    CoinDict['dec'] = round(float(float(coin['amount']) /IBCTokens.SATOSHI),4)
                elif IBCTokens.IBCATOM in coin['denom']:
                    CoinDict['atom'] = round(float(float(coin['amount']) /IBCTokens.SATOSHI),4)
                elif IBCTokens.IBCOSMO in coin['denom']:
                    CoinDict['osmo'] = round(float(float(coin['amount']) /IBCTokens.SATOSHI),4)
        except Exception as e:
            print(str(e))
            return None
        return CoinDict
    
    def get_ip_address(self):
        try:
            resolver = DNSRequests.MakeDNSRequest(domain=HTTParams.IPAPIDNS, timeout=5, lifetime=6.5)
            ifconfig = resolver.DNSRequest()
            if ifconfig:
                print("%s:%s" % (HTTParams.IPAPIDNS, ifconfig))
                Request = HTTPRequests.MakeRequest(TIMEOUT=7)
                http = Request.hadapter()
                req = http.get(HTTParams.IPAPI)
                ifJSON = req.json()
                print(ifJSON)
                with open(path.join(ConfParams.KEYRINGDIR, 'ip-api.json'), 'w') as f:
                    f.write(json.dumps(ifJSON))
                return True
                
            else:
                print("Error resolving ip-api.com... defaulting...")
                with open(path.join(ConfParams.KEYRINGDIR, 'ip-api.json'), 'w') as f:
                    f.write(json.dumps('{}'))
                return False
        except Exception as e:
            print(str(e))
            with open(path.join(ConfParams.KEYRINGDIR, 'ip-api.json'), 'w') as f:
                f.write(json.dumps('{}'))
            return False
                
    
        