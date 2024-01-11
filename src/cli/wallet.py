import pexpect
import json
import requests
import psutil
import binascii
import time
from time import sleep
from os import path, remove

from json.decoder import JSONDecodeError

from conf.meile_config import MeileGuiConfig
from typedef.konstants import IBCTokens
from typedef.konstants import ConfParams
from typedef.konstants import HTTParams
from adapters import HTTPRequests
from cli.v2ray import V2RayHandler

import base64
import uuid
import configparser

import bech32
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
from sentinel_protobuf.sentinel.subscription.v2.msg_pb2 import MsgCancelRequest, MsgCancelResponse

from sentinel_sdk.sdk import SDKInstance
from sentinel_sdk.types import NodeType, TxParams, Status
from sentinel_sdk.utils import search_attribute
from pywgkey import WgKey
from mnemonic import Mnemonic
from keyrings.cryptfile.cryptfile import CryptFileKeyring
import ecdsa
import hashlib

# from cosmpy.aerial.client import LedgerClient, NetworkConfig
# from cosmpy.aerial.wallet import LocalWallet
# from cosmpy.crypto.keypairs import PrivateKey
# from cosmpy.aerial.tx import Transaction
# from cosmpy.aerial.tx_helpers import TxResponse
# from cosmpy.aerial.client.utils import prepare_and_broadcast_basic_transaction

MeileConfig = MeileGuiConfig()
sentinelcli = MeileConfig.resource_path("../bin/sentinelcli")
v2ray_tun2routes_connect_bash = MeileConfig.resource_path("../bin/routes.sh")

class HandleWalletFunctions():
    connected =  {'v2ray_pid' : None, 'result' : False, 'status' : None}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)

    def __keyring(self, keyring_passphrase: str):
        kr = CryptFileKeyring()
        kr.filename = "keyring.cfg"
        print(ConfParams.KEYRINGDIR)
        kr.file_path = path.join(ConfParams.KEYRINGDIR, kr.filename)
        print(kr.file_path)
        kr.keyring_key = keyring_passphrase
        return kr

    def create(self, wallet_name, keyring_passphrase, seed_phrase = None):
        # Credtis: https://github.com/ctrl-Felix/mospy/blob/master/src/mospy/utils.py

        if seed_phrase is None:
            seed_phrase = Mnemonic("english").generate(strength=256)

        print(seed_phrase)  # TODO: only-4-debug
        seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
        bip44_def_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS).DeriveDefaultPath()

        privkey_obj = ecdsa.SigningKey.from_string(bip44_def_ctx.PrivateKey().Raw().ToBytes(), curve=ecdsa.SECP256k1)
        pubkey  = privkey_obj.get_verifying_key()
        s = hashlib.new("sha256", pubkey.to_string("compressed")).digest()
        r = hashlib.new("ripemd160", s).digest()
        five_bit_r = bech32.convertbits(r, 8, 5)
        account_address = bech32.bech32_encode("sent", five_bit_r)
        print(account_address)

        # Create a class of separated method for keyring please
        kr = self.__keyring(keyring_passphrase)
        kr.set_password("meile-gui", wallet_name, bip44_def_ctx.PrivateKey().Raw().ToBytes().hex())

        return {
            'address': account_address,
            'seed': seed_phrase
        }


    def subscribe(self, KEYNAME, NODE, DEPOSIT, GB, hourly):
        if not KEYNAME:  # TODO: (?)
            return (False, 1337)

        print("Deposit/denom")
        print(DEPOSIT)
        DENOM = self.DetermineDenom(DEPOSIT)
        print(DENOM)

        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        PASSWORD = CONFIG['wallet'].get('password', '')

        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)

        grpc = self.GRPC.replace("grpc+http://", "").replace("/", "")  # TODO: why const is grpc is saved as ... (?)
        grpcaddr, grpcport = grpc.split(":")

        kr = self.__keyring(PASSWORD)
        private_key = kr.get_password("meile-gui", KEYNAME)  # TODO: very ungly

        print(private_key)  # TODO: only-4-debug
        sdk = SDKInstance(grpcaddr, int(grpcport), secret=private_key)

        # From ConfParams
        # GASPRICE         = "0.2udvpn"
        # GASADJUSTMENT    = 1.15
        # GAS              = 500000
        # ConfParams.GASPRICE, ConfParams.GAS, ConfParams.GASADJUSTMENT,

        tx_params = TxParams(
            # denom="udvpn",  # TODO: from ConfParams
            # fee_amount=20000,  # TODO: from ConfParams
            # gas=ConfParams.GAS,
            gas_multiplier=ConfParams.GASADJUSTMENT
        )

        print("node_address", NODE)
        print("gigabytes", 0 if hourly else GB)  # TODO: review this please
        print("hours", GB if hourly else 0)  # TODO: review this please
        print("denom", DENOM)
        print("tx_params", tx_params)

        tx = sdk.nodes.SubscribeToNode(
            node_address=NODE,
            gigabytes=0 if hourly else GB,  # TODO: review this please
            hours=GB if hourly else 0,  # TODO: review this please
            denom=DENOM,
            tx_params=tx_params,
        )
        if tx.get("log", None) is not None:
            return(False, tx["log"])

        if tx.get("hash", None) is not None:
            tx_response = sdk.nodes.wait_transaction(tx["hash"])
            print(tx_response)
            subscription_id = search_attribute(
                tx_response, "sentinel.node.v2.EventCreateSubscription", "id"
            )
            if subscription_id:
                return (True,0)

        return(False, "Tx error")

        # return self.ParseSubscribe()

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

        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)

        grpc = self.GRPC.replace("grpc+http://", "").replace("/", "")  # TODO: why const is grpc is saved as ... (?)
        grpcaddr, grpcport = grpc.split(":")

        kr = self.__keyring(PASSWORD)
        private_key = kr.get_password("meile-gui", KEYNAME)  # TODO: very ungly

        print(private_key)  # TODO: only-4-debug
        sdk = SDKInstance(grpcaddr, int(grpcport), secret=private_key)

        # From ConfParams
        # GASPRICE         = "0.2udvpn"
        # GASADJUSTMENT    = 1.15
        # GAS              = 500000
        # ConfParams.GASPRICE, ConfParams.GAS, ConfParams.GASADJUSTMENT,

        tx_params = TxParams(
            # denom="udvpn",  # TODO: from ConfParams
            # fee_amount=20000,  # TODO: from ConfParams
            # gas=ConfParams.GAS,
            gas_multiplier=ConfParams.GASADJUSTMENT
        )
        tx = sdk.subscriptions.Cancel(subId, tx_params=tx_params)
        tx_height = 0
        if tx.get("log", None) is None:
            tx_response = sdk.nodes.wait_transaction(tx["hash"])
            tx_height = tx_response.tx_response.height

        message = f"Unsubscribe from Subscription ID: {subId}, was successful at Height: {tx_height}" if tx.get("log", None) is None else tx.get["log"]
        return {'hash' : tx.get("hash", None), 'success' : tx.get("log", None) is None, 'message' : message}


    def connect(self, ID, address, type):
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        PASSWORD = CONFIG['wallet'].get('password', '')
        KEYNAME = CONFIG['wallet'].get('keyname', '')

        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)

        grpc = self.GRPC.replace("grpc+http://", "").replace("/", "")  # TODO: why const is grpc is saved as ... (?)
        grpcaddr, grpcport = grpc.split(":")

        kr = self.__keyring(PASSWORD)
        private_key = kr.get_password("meile-gui", KEYNAME)  # TODO: very ungly

        print(private_key)  # TODO: only-4-debug
        sdk = SDKInstance(grpcaddr, int(grpcport), secret=private_key)

        # From ConfParams
        # GASPRICE         = "0.2udvpn"
        # GASADJUSTMENT    = 1.15
        # GAS              = 500000
        # ConfParams.GASPRICE, ConfParams.GAS, ConfParams.GASADJUSTMENT,

        tx_params = TxParams(
            # denom="udvpn",  # TODO: from ConfParams
            # fee_amount=20000,  # TODO: from ConfParams
            # gas=ConfParams.GAS,
            gas_multiplier=ConfParams.GASADJUSTMENT
        )

        sessions = sdk.sessions.QuerySessionsForSubscription(int(ID))
        for session in sessions:
            if session.status == Status.ACTIVE.value:
                tx = sdk.sessions.EndSession(session_id=session.id, rating=0, tx_params=tx_params)
                print(sdk.sessions.wait_transaction(tx["hash"]))

        tx = sdk.sessions.StartSession(subscription_id=int(ID), address=address)
        if tx.get("log", None) is not None:
            self.connected = {"v2ray_pid" : None,  "result": False, "status" : tx["log"]}
            print(self.connected)
            return

        tx_response = sdk.sessions.wait_transaction(tx["hash"])
        session_id = search_attribute(tx_response, "sentinel.session.v2.EventStart", "id")

        time.sleep(1)  # Wait a few seconds....
        # The sleep is required because the session_id could not be fetched from the node / rpc

        node = sdk.nodes.QueryNode(address)

        # response = sdk.nodes.PostSession(int(session_id), node.remote_url, NodeType.WIREGUARD if type == "WireGuard" else NodeType.V2RAY)
        # re-implement here sdk.nodes.PostSession ...

        if type == "WireGuard":
            # [from golang] wgPrivateKey, err = wireguardtypes.NewPrivateKey()
            # [from golang] key = wgPrivateKey.Public().String()
            wgkey = WgKey()
            # The private key should be used by the wireguard client
            key = wgkey.pubkey
        else:  # NodeType.V2RAY
            # os.urandom(16)
            # [from golang] uid, err = uuid.GenerateRandomBytes(16)
            # [from golang] key = base64.StdEncoding.EncodeToString(append([]byte{0x01}, uid...))
            key = base64.b64encode(uuid.uuid4().bytes).decode("utf-8")

        sk = ecdsa.SigningKey.from_string(
            sdk._account.private_key, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256
        )

        session_id = int(session_id)
        # Uint64ToBigEndian
        bige_session = session_id.to_bytes(8, "big")
        signature = sk.sign(bige_session)

        payload = {
            "key": key,
            "signature": base64.b64encode(signature).decode("utf-8"),
        }
        response = requests.post(f"{node.remote_url}/accounts/{sdk._account.address}/sessions/{session_id}", json=payload, headers={"Content-Type": "application/json; charset=utf-8"}, verify=False)
        if response.ok is False:
            self.connected = {"v2ray_pid" : None,  "result": False, "status" : response.text}
            print(self.connected)
            return
        
        response = response.json()
        if response.get("success", True) is True:
            decode = base64.b64decode(response["result"])

            address = f"{decode[0]}.{decode[1]}.{decode[2]}.{decode[3]}/32"
            host = f"{decode[20]}.{decode[21]}.{decode[22]}.{decode[23]}"
            port = (decode[24] & -1) << 8 | decode[25] & -1
            peer_endpoint = f"{host}:{port}"

            print("address", address)
            print("host", host)
            print("port", port)
            print("peer_endpoint", peer_endpoint)

            public_key = base64.b64encode(decode[26:58]).decode("utf-8")
            print("public_key", public_key)

            config = configparser.ConfigParser()
            config.optionxform = str

            config.add_section("Interface")
            config.set("Interface", "Address", address)
            config.set("Interface", "PrivateKey", wgkey.privkey)
            # config.set("Interface", "DNS", "1.1.1.1")
            config.add_section("Peer")
            config.set("Peer", "PublicKey", public_key)
            config.set("Peer", "Endpoint", peer_endpoint)
            config.set("Peer", "AllowedIPs", "0.0.0.0/0")
            config.set("Peer", "PersistentKeepalive", "25")

            iface = "wg99"
            config_file = path.join(ConfParams.BASEDIR, f"{iface}.conf")

            if path.isfile(config_file) is True:
                remove(config_file)

            with open(config_file, "w", encoding="utf-8") as example:
                config.write(example)

            import subprocess
            # Workaround only for Linux, just for test please :)
            subprocess.Popen(
                f"ip link delete {iface}".split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).wait()
            subprocess.Popen(
                f"wg-quick up {config_file}".split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).wait()

            if psutil.net_if_addrs().get(iface):
                self.connected = {"v2ray_pid" : None,  "result": True, "status" : iface}
                return

            self.connected = {"v2ray_pid" : None,  "result": False, "status" : "Error bringing up wireguard interface"}
            return


        connCMD = "pkexec env PATH=%s %s connect --home %s --keyring-backend file --keyring-dir %s --chain-id %s --node %s --gas-prices %s --gas %d --gas-adjustment %f --yes --from '%s' %s %s" % (ConfParams.PATH,
                                                                                                                                                                                                    sentinelcli,
                                                                                                                                                                                                    ConfParams.BASEDIR,
                                                                                                                                                                                                    ConfParams.KEYRINGDIR,
                                                                                                                                                                                                    ConfParams.CHAINID,
                                                                                                                                                                                                    self.RPC,
                                                                                                                                                                                                    ConfParams.GASPRICE,
                                                                                                                                                                                                    ConfParams.GAS,
                                                                                                                                                                                                    ConfParams.GASADJUSTMENT,
                                                                                                                                                                                                    KEYNAME,
                                                                                                                                                                                                    ID,
                                                                                                                                                                                                    address)

        print(connCMD)
        ofile =  open(ConfParams.CONNECTIONINFO, "wb")

        try:
            child = pexpect.spawn(connCMD)
            child.logfile = ofile

            child.expect(".*")
            child.sendline(PASSWORD)
            child.expect(pexpect.EOF)

            ofile.flush()
            ofile.close()
        except pexpect.exceptions.TIMEOUT:
            self.connected = {"v2ray_pid" : None,  "result": False, "status" : "Error running expect"}
            return


        with open(ConfParams.CONNECTIONINFO, "r") as connection_file:
            lines = connection_file.readlines()

            for l in lines:
                if "Error" in l and "v2ray" not in l and "inactive_pending" not in l:
                    self.connected = {"v2ray_pid" : None,  "result": False, "status" : l}
                    return

        if type == "WireGuard":
            if psutil.net_if_addrs().get("wg99"):
                self.connected = {"v2ray_pid" : None,  "result": True, "status" : "wg99"}
                return
            else:
                self.connected = {"v2ray_pid" : None,  "result": False, "status" : "Error bringing up wireguard interface"}
                return
        else:
            TUNIFACE = False
            V2Ray = V2RayHandler(v2ray_tun2routes_connect_bash + " up")
            V2Ray.start_daemon()
            sleep(15)

            for iface in psutil.net_if_addrs().keys():
                if "tun" in iface:
                    TUNIFACE = True
                    break

            if TUNIFACE:
                self.connected = {"v2ray_pid" : V2Ray.v2ray_pid, "result": True, "status" : TUNIFACE}
                print(self.connected)
                return
            else:
                try:
                    V2Ray.v2ray_script = v2ray_tun2routes_connect_bash + " down"
                    V2Ray.kill_daemon()
                    #V2Ray.kill_daemon()
                    #Tun2Socks.kill_daemon()
                except Exception as e:
                    print(str(e))

                self.connected = {"v2ray_pid" : V2Ray.v2ray_pid,  "result": False, "status": "Error connecting to v2ray node: %s" % TUNIFACE}
                print(self.connected)
                return

    def get_balance(self, address):
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        endpoint = HTTParams.BALANCES_ENDPOINT + address
        CoinDict = {'dvpn' : 0, 'scrt' : 0, 'dec'  : 0, 'atom' : 0, 'osmo' : 0}
        #CoinDict = {'tsent' : 0, 'scrt' : 0, 'dec'  : 0, 'atom' : 0, 'osmo' : 0}

        try:
            r = http.get(HTTParams.APIURL + endpoint)
            coinJSON = r.json()
        except:
            return None

        print(coinJSON)
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




