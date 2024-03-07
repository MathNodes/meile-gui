import pexpect
import json
import requests
import psutil
import binascii
import random
import re
from time import sleep
from os import path, remove
from urllib.parse import urlparse
from grpc import RpcError

from json.decoder import JSONDecodeError

from conf.meile_config import MeileGuiConfig
from typedef.konstants import IBCTokens, ConfParams, HTTParams
from adapters import HTTPRequests
from cli.v2ray import V2RayHandler, V2RayConfiguration

import base64
import uuid
import configparser
import socket
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


        grpcaddr, grpcport = urlparse(self.GRPC).netloc.split(":")

        kr = self.__keyring(PASSWORD)
        private_key = kr.get_password("meile-gui", KEYNAME)  # TODO: very ungly

        print(private_key)  # TODO: only-4-debug
        sdk = SDKInstance(grpcaddr, int(grpcport), secret=private_key)

        # From ConfParams
        # GASPRICE         = "0.2udvpn"
        # GASADJUSTMENT    = 1.15
        # GAS              = 500000
        # ConfParams.GASPRICE, ConfParams.GAS, ConfParams.GASADJUSTMENT,

        balance = self.get_balance(sdk._account.address)

        amount_required = float(DEPOSIT.replace(DENOM, ""))
        token_ibc = {v: k for k, v in IBCTokens.IBCUNITTOKEN.items()}
        # Balance keys are dvpn, src, dec etc, alredy / /IBCTokens.SATOSHI
        # We could paramtrize that method and ask if we want dvpn or udvpn
        # For the moment leave as is
        # [1:] remove the 'u'
        ubalance = balance.get(token_ibc[DENOM][1:], 0) * IBCTokens.SATOSHI
        # < amount_required what about the fee and gas?
        if ubalance < amount_required:
            return(False, f"Balance is too low, required: {round(amount_required / IBCTokens.SATOSHI, 4)}{token_ibc[DENOM][1:]}")

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
            tx_response = sdk.nodes.wait_for_tx(tx["hash"])
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


        grpcaddr, grpcport = urlparse(self.GRPC).netloc.split(":")

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
        tx_height = 0

        try:
            tx = sdk.subscriptions.Cancel(subId, tx_params=tx_params)
        except RpcError as rpc_error:
            details = rpc_error.details()  # pylint: disable=no-member
            # TODO: the following prints are only for debug
            print("details", details)
            print("code", rpc_error.code())  # pylint: disable=no-member
            print("debug_error_string", rpc_error.debug_error_string())  # pylint: disable=no-member

            search = f"invalid status inactive_pending for subscription {subId}"
            if re.search(search, details, re.IGNORECASE):
                message = "Cannot unsubscribe. Pending session still on blockchain. Try your request again later."
            else:
                message = "Error connecting to gRPC server. Try your request again later."

            return {'hash' : None, 'success' : False, 'message' : message}

        if tx.get("log", None) is None:
            tx_response = sdk.nodes.wait_for_tx(tx["hash"])
            tx_height = tx_response.tx_response.height

        message = f"Unsubscribe from Subscription ID: {subId}, was successful at Height: {tx_height}" if tx.get("log", None) is None else tx.get["log"]
        return {'hash' : tx.get("hash", None), 'success' : tx.get("log", None) is None, 'message' : message}


    def connect(self, ID, address, type):
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        PASSWORD = CONFIG['wallet'].get('password', '')
        KEYNAME = CONFIG['wallet'].get('keyname', '')

        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)


        grpcaddr, grpcport = urlparse(self.GRPC).netloc.split(":")

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
                print(sdk.sessions.wait_for_tx(tx["hash"]))

        tx = sdk.sessions.StartSession(subscription_id=int(ID), address=address)
        if tx.get("log", None) is not None:
            self.connected = {"v2ray_pid" : None,  "result": False, "status" : tx["log"]}
            print(self.connected)
            return

        tx_response = sdk.sessions.wait_for_tx(tx["hash"])
        session_id = search_attribute(tx_response, "sentinel.session.v2.EventStart", "id")

        from_event = {
            "subscription_id": search_attribute(tx_response, "sentinel.session.v2.EventStart", "subscription_id"),
            "address": search_attribute(tx_response, "sentinel.session.v2.EventStart", "address"),
            "node_address": search_attribute(tx_response, "sentinel.session.v2.EventStart", "node_address"),
        }
        # Double check :)
        assert from_event["subscription_id"] == ID and from_event["address"] == sdk._account.address and from_event["node_address"] == address

        sleep(1)  # Wait a few seconds....
        # The sleep is required because the session_id could not be fetched from the node / rpc

        node = sdk.nodes.QueryNode(address)
        assert node.address == address

        # response = sdk.nodes.PostSession(int(session_id), node.remote_url, NodeType.WIREGUARD if type == "WireGuard" else NodeType.V2RAY)
        # re-implement here sdk.nodes.PostSession ...

        if type == "WireGuard":
            # [from golang] wgPrivateKey, err = wireguardtypes.NewPrivateKey()
            # [from golang] key = wgPrivateKey.Public().String()
            wgkey = WgKey()
            # The private key should be used by the wireguard client
            key = wgkey.pubkey
        else:  # NodeType.V2RAY
            # [from golang] uid, err = uuid.GenerateRandomBytes(16)
            uid_16b = uuid.uuid4()
            # [from golang] key = base64.StdEncoding.EncodeToString(append([]byte{0x01}, uid...))
            # data length must be 17 bytes...
            key = base64.b64encode(bytes(0x01) + uid_16b.bytes).decode("utf-8")

        # Sometime we get a random "code":4,"message":"invalid signature ...``
        for _ in range(0, 3):  # 3 as max_attempt:
            sk = ecdsa.SigningKey.from_string(sdk._account.private_key, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)

            # Uint64ToBigEndian
            bige_session = int(session_id).to_bytes(8, byteorder="big")

            signature = sk.sign(bige_session)
            payload = {
                "key": key,
                "signature": base64.b64encode(signature).decode("utf-8"),
            }
            print(payload)
            response = requests.post(
                f"{node.remote_url}/accounts/{sdk._account.address}/sessions/{session_id}",
                json=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                verify=False,
                timeout=60  # TODO: configurable
            )
            print(response, response.text)
            if response.ok is True:
                break

            sleep(random.uniform(0.5, 1))
            # Continue ireation only for code == 4 (invalid signature)
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
                config.set("Interface", "DNS", ",".join(["10.8.0.1","1.0.0.1","1.1.1.1"]))  # TODO: 8.8.8.8 (?)
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

                child = pexpect.spawn(f"pkexec sh -c 'ip link delete {iface}; wg-quick up {config_file}'")
                child.expect(pexpect.EOF)

                if psutil.net_if_addrs().get(iface):
                    self.connected = {"v2ray_pid" : None,  "result": True, "status" : iface}
                    return
            else:  # v2ray
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
                print("vmess_uid", f"{uid_16b}")
                print("vmess_transport", vmess_transports[decode[-1]])

                v2ray_config = V2RayConfiguration(
                    api_port=api_port,
                    vmess_port=vmess_port,
                    vmess_address=vmess_address,
                    vmess_uid=f"{uid_16b}",
                    vmess_transport=vmess_transports[decode[-1]],
                    proxy_port=1080
                )
                # ConfParams.KEYRINGDIR (.meile-gui)
                config_file = path.join(ConfParams.KEYRINGDIR, "v2ray_config.json")
                if path.isfile(config_file) is True:
                    remove(config_file)
                with open(config_file, "w", encoding="utf-8") as f:
                    f.write(json.dumps(v2ray_config.get(), indent=4))

                # v2ray_tun2routes_connect_bash
                # >> hardcoded = proxy port >> 1080
                # >> hardcoded = v2ray file >> /home/${USER}/.meile-gui/v2ray_config.json

                tuniface = False
                v2ray_handler = V2RayHandler(f"{v2ray_tun2routes_connect_bash} up")
                v2ray_handler.start_daemon()
                sleep(15)

                for iface in psutil.net_if_addrs().keys():
                    if "tun" in iface:
                        tuniface = True
                        break

                if tuniface is True:
                    self.connected = {"v2ray_pid" : v2ray_handler.v2ray_pid, "result": True, "status" : tuniface}
                    print(self.connected)
                    return
                else:
                    try:
                        v2ray_handler.v2ray_script = f"{v2ray_tun2routes_connect_bash} down"
                        v2ray_handler.kill_daemon()
                    except Exception as e:
                        print(str(e))

                    self.connected = {"v2ray_pid" : v2ray_handler.v2ray_pid,  "result": False, "status": f"Error connecting to v2ray node: {tuniface}"}
                    print(self.connected)
                    return

        self.connected = {"v2ray_pid" : None,  "result": False, "status": "boh"}
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




