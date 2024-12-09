import collections
from os import path
import re
import requests
from requests.exceptions import ReadTimeout, ConnectionError, HTTPError
from urllib3.exceptions import InsecureRequestWarning, ResponseError
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime,timedelta
import time
from urllib.parse import urlparse
import copy
from copy import deepcopy
import random

from treelib import  Tree
from treelib.exceptions import DuplicatedNodeIdError

from geography.continents import OurWorld
from conf.meile_config import MeileGuiConfig
from typedef.konstants import ConfParams, HTTParams, IBCTokens, TextStrings, NodeKeys
from adapters import HTTPRequests
from cli.v2ray import V2RayHandler
from helpers import helpers

import mospy
import grpc
from grpc import RpcError, StatusCode
from sentinel_sdk.sdk import SDKInstance
from sentinel_sdk.types import PageRequest, Status
from builtins import AttributeError

MeileConfig = MeileGuiConfig()
v2ray_tun2routes_connect_bash = path.join(ConfParams.KEYRINGDIR, "bin/routes.sh")

class NodeTreeData():
    BackupNodeTree = None
    NodeTree       = None
    SubResult      = []
    NodeScores     = {}
    NodeLocations  = {}
    NodeTypes      = {}
    NodeHealth     = {}
    NodeFormula    = {}
    
    def __init__(self, node_tree):
        if not node_tree:
            self.NodeTree = Tree()
        else:
            self.NodeTree = node_tree
            
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        self.MNAPI = CONFIG['network'].get('mnapi', HTTParams.SERVER_URL)
        
    def get_api_server(self):
        Request = HTTPRequests.MakeRequest(TIMEOUT=10) # long timeout in case there is heavy load
        http = Request.hadapter()
        
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.MNAPI = CONFIG['network'].get('mnapi', HTTParams.SERVER_URL)
        
        try:
            if HTTParams.SERVER_URL != self.MNAPI: 
                resp = http.get(self.MNAPI + HTTParams.CACHE_ENDPOINT)
            else:
                resp = http.get(HTTParams.SERVER_URL + HTTParams.CACHE_ENDPOINT)
            ipapi_json = resp.json()
        except Exception as e:
            print(str(e))
            return HTTParams.NODE_API[random.randint(0, len(HTTParams.NODE_API) -1)]
        
        
        client_country = ipapi_json['country']
        client_continent = OurWorld.our_world.get_country_continent_code(client_country.lower())
        print(f"IP-API: {client_country},{client_continent}")
        try:
            resp = http.get(HTTParams.SERVER_URL + HTTParams.CACHE_ENDPOINT)
            cache_json = resp.json()
            
        except Exception as e:
            print(str(e))
            return HTTParams.NODE_API[random.randint(0, len(HTTParams.NODE_API) -1)]
        
        cache_urls = []
        country_urls = []
        for server in cache_json:
            if client_country.lower() == server['country'].lower():
                country_urls.append(server['url'])
            elif client_continent == server['continent']:
                cache_urls.append(server['url'])
            elif client_continent == "oc" and server['continent'] == "as":
                cache_urls.append(server['url'])
            elif client_continent == "sa" and server['continent'] == "na":
                cache_urls.append(server['url'])
            elif client_continent == "af" and server['continent'] == 'eu':
                cache_urls.append(server['url'])
        
        if len(country_urls) > 0:
            return country_urls[random.randint(0, len(country_urls) -1)]
        elif len(cache_urls) == 1:
            return cache_urls[0]
        else:
            return cache_urls[random.randint(0, len(cache_urls) -1)]

        
    def get_nodes(self, latency, *kwargs):
        AllNodesInfo = []
        ninfos       = []
        data = []
        
        CACHE_SERVER = self.get_api_server()
        # Use Cache Server for faster loading.  
        Request = HTTPRequests.MakeRequest(TIMEOUT=23) # long timeout in case there is heavy load
        http = Request.hadapter()
        retries = 0
        while True and retries < 5:
            try:
                #N = random.randint(0, len(HTTParams.NODE_API) -1)
                try: 
                    r = http.get(CACHE_SERVER)
                    r.raise_for_status()
                except (ReadTimeout, ConnectionError, HTTPError):
                    print(f"Server error for {CACHE_SERVER}. Switching to backup server.")
                    CACHE_SERVER = HTTParams.NODE_APIS[random.randint(0, len(HTTParams.NODE_APIS)-1)] 
                    continue
                except requests.RequestException as e:
                    print(f"Server error for {CACHE_SERVER}. Switching to backup server.")
                    CACHE_SERVER = HTTParams.NODE_APIS[random.randint(0, len(HTTParams.NODE_APIS)-1)] 
                    continue
                data = r.json()
                if not data:
                    retries += 1
                    if retries >= 2:
                        CACHE_SERVER = HTTParams.NODE_APIS[random.randint(0, len(HTTParams.NODE_APIS)-1)]
                    continue
                #rint(data)
                for node in data:
                    ninfos.append(node['moniker'])
                    ninfos.append(node['node_address'])
                    ninfos.append(node['gigabyte_prices'])
                    ninfos.append(node['hourly_prices'])
                    if "The Netherlands" in node['country']:
                        node['country'] = "Netherlands"
                    elif "Czech Republic" in node['country']:
                        node['country'] = "Czechia"
                    ninfos.append(node['country'])
                    ninfos.append(node['city'])
                    ninfos.append(node['latitude'])
                    ninfos.append(node['longitude'])
                    ninfos.append(node['bandwidth_down'])
                    ninfos.append(node['bandwidth_up'])
                    ninfos.append(node['connected_peers'])
                    ninfos.append(node['max_peers'])
                    ninfos.append(node['handshake'])
                    ninfos.append("WireGuard" if node['node_type'] == 1 else "V2Ray")
                    ninfos.append(node['node_version'])
                    ninfos.append(node['isp_type'])
                    ninfos.append(node['score'])
                    ninfos.append(node['votes'])
                    ninfos.append(node['formula'])
                    AllNodesInfo.append(dict(zip(NodeKeys.NodesInfoKeys, ninfos)))
                    ninfos.clear()
                break
            except Exception as e:
                print(str(e))
                data = []
                break
        
        AllNodesInfoSorted = sorted(AllNodesInfo, key=lambda d: d[NodeKeys.NodesInfoKeys[4]])
        
        self.NodeTree = self.CreateNodeTreeStructure(data)
        
        #print(AllNodesInfoSorted)
        
        for d in AllNodesInfoSorted:
            
            '''Parse out old node versions < 0.7.0'''   
            
            d[NodeKeys.NodesInfoKeys[14]] = d[NodeKeys.NodesInfoKeys[14]].split('-')[0]
            #version = d[NodeKeys.NodesInfoKeys[14]].replace('.','')
            #if version not in NodeKeys.NodeVersions:
            #    continue
            
            # Gigabyte Prices
            d[NodeKeys.NodesInfoKeys[2]] = self.return_denom(d[NodeKeys.NodesInfoKeys[2]])
            d[NodeKeys.NodesInfoKeys[2]] = self.parse_coin_deposit(d[NodeKeys.NodesInfoKeys[2]])
            
            # Hourly Prices
            d[NodeKeys.NodesInfoKeys[3]] = self.return_denom(d[NodeKeys.NodesInfoKeys[3]])
            d[NodeKeys.NodesInfoKeys[3]] = self.parse_coin_deposit(d[NodeKeys.NodesInfoKeys[3]])
            

            try:
                self.NodeTree.create_node(d[NodeKeys.NodesInfoKeys[1]], d[NodeKeys.NodesInfoKeys[1]],parent=d[NodeKeys.NodesInfoKeys[4]], data=d )
            except Exception as e:
                print(str(e)) # print the exception in this early build to identify any issues building the nodetree
                pass
        
        # Used for Search and Plans
        self.BackupNodeTree = copy.deepcopy(self.NodeTree)            
        
        # For pretty output. Unicode is used in treelib > 1.6.1     
        self.NodeTree.show()
        
    # Filter nodetree.
    # key;              what we want to filter, for example: Moniker, Type, Health
    # value;            query value
    # between;          value must be between[0], between[1], for example:
    #                   key = "Hourly Price", between = ("5.3426dvpn", "15.3426dvpn")
    #                   key = "Scores", between = (8, 10)
    # from_backup;      if true it will be used the backupped data, else will be used the 'renderized' one (maybe already filtered)
    # perfect_match;    if true, value must be equal for example:
    #                   perfect_match = True, key = "Moniker", value = "Pinco" will match only Moniker === Pinco
    #                   perfect_match = False, key = "Moniker", value = "Pinco" will match only Moniker like Pincopallo, Pizzapinco10, Pincopallino, Pinco1


    def restore_tree(self):
        self.NodeTree = copy.deepcopy(self.BackupNodeTree)
        
    def search(self, key: str, value = None, between: tuple = (), from_backup: bool = True, perfect_match: bool = False, is_list: bool = False):
        NodeAddressBool = False
        
        if value is None and len(between) == 0:
            # at least one of value or between must be setted
            return

        amount_rx = r'^(\.\d|\d+\.\d+|\d+)'
        #key = key.title()

        # Prepare the "between" values out of iteration
        if value is None and len(between) == 2:
            a, b = between[0], between[1]
            if key in ['Hourly Price', 'Price']:
                a = amount_denon_dict(a)
                b = amount_denon_dict(b)
                # print(f"[DEBUG] a: {a}, b: {b}")

                if a is None or b is None:
                    # unable to continue
                    return

                if a["denom"] != b["denom"]:
                    # unable to use different denom in between
                    return

                # It the same of b["denom"], just a variable rename
                def_denom = a["denom"]
                if def_denom == "udvpn":
                    # btw, probably no one will use udvpn as search field
                    a["denom"] = b["denom"] = "dvpn"
                    a["amount"] = a["amount"] // 1000000
                    b["amount"] = b["amount"] // 1000000
            else:
                a = float(re.search(amount_rx, a).group(0))
                b = float(re.search(amount_rx, b).group(0))

        # Create a copy of Tree please ...
        # Under the iteration of keys I will delete all the nodes that doesn't match our query
        filtered = copy.deepcopy(self.BackupNodeTree if from_backup is True else self.NodeTree)
        # Iteration via the original data, in order to prevent "RuntimeError: dictionary changed size during iteration"
        for identifier, content in (self.BackupNodeTree if from_backup is True else self.NodeTree).nodes.items():
            if identifier.startswith("sentnode"):
                #print(content.data)
                #print(key)
                if key in content.data:
                    print(f"Key in data: {key}")
                    # use in... / wherlike / contains
                    if value:
                        #print(f"Value: {value}")
                        if is_list:
                            for v in value:
                                if v == str(identifier):
                                    NodeAddressBool = True
                                    break
                                else:
                                    NodeAddressBool = False
                            if not NodeAddressBool:    
                                if perfect_match is True:
                                    if v.lower().strip() != content.data[key].lower():
                                        filtered.remove_node(identifier)
                                elif v.lower().strip() not in content.data[key].lower():
                                    # use in... / wherlike / contains
                                    filtered.remove_node(identifier)
                        else:
                            try: 
                                if perfect_match is True:
                                    if value.lower().strip() != content.data[key].lower():
                                        filtered.remove_node(identifier)
                                elif value.lower().strip() not in content.data[key].lower():
                                    # use in... / wherlike / contains
                                    #print(f"Revmoving: {identifier}")
                                    filtered.remove_node(identifier)
                            except AttributeError:
                                continue
                    elif len(between) == 2:

                        # ups, following this: https://github.com/MathNodes/meile-gui/commit/622e501d332f0a34009b77548c4672e0ae32577b#diff-3729b5451a4398b2a4fd75a4bf0062d9bd5040677dd766ade023084aa9c03379R87
                        # NodesInfoKeys = ["Moniker","Address","Price","Hourly Price", "Country","Speed","Latency","Peers","Handshake","Type","Version","Status"]
                        # NodesInfoKeys = ["Moniker","Address","Price","Hourly Price", "Country","City","Latitude","Longitude","Download","Upload","Peers","Max Peers","Handshake","Type","Version"]

                        # I'm so crazy and I like it
                        if key in ['Hourly Price', 'Price']:
                            # 'Hourly Price': '0.0185scrt,0.0008atom,1.8719dec,0.0189osmo,4.16dvpn',
                            # 'Price': '0.0526scrt,0.0092atom,1.1809dec,0.1227osmo,15.3426dvpn',
                            prices = content.data[key].split(",")
                            # Now we have an array: ['0.0185scrt', '0.0008atom', '1.8719dec', '0.0189osmo', '4.16dvpn']
                            # Convert array with denom as key and amount as value:
                            prices = {
                                amount_denon_dict(p)["denom"]: amount_denon_dict(p)["amount"] for p in prices
                            }
                            # print(f"[DEBUG] {identifier} | prices: {prices}")
                            if def_denom not in prices:
                                # uhm, unable to continue, probably the node doesn't support this denom (?)
                                # remove anyway from the tree
                                filtered.remove_node(identifier)
                            else:
                                # Make sure a is min and b is max
                                _min = min(a["amount"], b["amount"])
                                _max = max(a["amount"], b["amount"])
                                if prices[def_denom] > _max or prices[def_denom] < _min:
                                    # print(f"[DEBUG] {identifier} | remove basecause > {_max} (max) or < {_min} (min)")
                                    filtered.remove_node(identifier)
                        else:
                            # 'Latency': '1.762s',
                            # 'Peers': '0',
                            # --> not managed: 'Speed': '123.93MB+520.20MB',

                            #Extract only number
                            node_value = float(re.search(amount_rx, content.data[key]).group(0))
                            # Make sure a is min and b is max
                            _min = min(a, b)
                            _max = max(a, b)
                            if node_value > _max or node_value < _min:
                                filtered.remove_node(identifier)


                # Type: wireguard / v2ray
                # Type: residential / hosting .... (uhmm) - ConnectionType
                # unnecessary since all data is pulled from one query from cache server
                '''
                elif key == "ConnectionType":
                    if identifier not in self.NodeTypes:
                        filtered.remove_node(identifier)
                    else:
                        if self.NodeTypes[identifier] != value:
                            filtered.remove_node(identifier)
                elif key == "Health":
                    if identifier not in self.NodeHealth:
                        filtered.remove_node(identifier)
                    else:
                        as_bool = value if isinstance(value, bool) else (value.lower() == "true")
                        if self.NodeHealth[identifier] != as_bool:
                            filtered.remove_node(identifier)
                elif key == "Scores":
                    if identifier not in self.NodeScores:
                        filtered.remove_node(identifier)
                    else:
                        rating = float(self.NodeScores[identifier][0])
                        if value is not None and float(value) != rating:
                            filtered.remove_node(identifier)
                        elif len(between) == 2:
                            # Make sure a is min and b is max
                            _min = min(a, b)
                            _max = max(a, b)
                            if rating > _max or rating < _min:
                                filtered.remove_node(identifier)
                '''
        # Always override the 'renderized' one (maybe already filtered)
        self.NodeTree = filtered
        
        # debug
        self.NodeTree.show()
        
    def CreateNodeTreeStructure(self, data, **kwargs):
        NodeTreeBase = Tree()
        RootTag = "SENTINEL"
        RootIdentifier = RootTag.lower()
        NodeTreeBase.create_node(RootTag, RootIdentifier)
        
        for node in data:
            if "The Netherlands" in node['country']:
                node['country'] = "Netherlands"
            elif "Czech Republic" in node['country']:
                node['country'] = "Czechia"
            
            c = node['country']
            try:
                if NodeTreeBase.contains(c):
                    continue
                else:
                    NodeTreeBase.create_node(c, c, parent=RootIdentifier)
            except DuplicatedNodeIdError:
                continue 

        return NodeTreeBase
    
    def return_denom(self, tokens):
        for ibc_coin in IBCTokens.IBCCOINS:
            for denom,ibc in ibc_coin.items():
                if ibc in tokens:
                    tokens = tokens.replace(ibc, denom)
        
        return tokens
    
    def parse_coin_deposit(self, tokens):
        UnitAmounts = []
        tokenString = ""
        pattern = r"([0-9]+)"

        if tokens.isspace() or not tokens:
            return ' '

        elif ',' in tokens:
            for deposit in tokens.split(','):
                amt = re.split(pattern,deposit)
                UnitAmounts.append(amt)
        else:
            amt = re.split(pattern,tokens)
            UnitAmounts.append(amt)

        for u in UnitAmounts:
            tokenString += str(round(float(float(u[1]) / IBCTokens.SATOSHI),4)) + str(IBCTokens.UNITTOKEN[u[2]]) + ','

        return tokenString[0:-1]
    
    def get_subscriptions(self, ADDRESS):
        SubsNodesInfo = []
        SubsFinalResult    = []
        print("Geting Subscriptions... %s" % ADDRESS)
        
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)
        grpcaddr, grpcport = self.GRPC.split(":")
        
        try:
            sdk = SDKInstance(grpcaddr, int(grpcport), ssl=True)
        except grpc._channel._InactiveRpcError as e:
            status_code = e.code()
            
            if status_code == StatusCode.NOT_FOUND:
                self.message = "Wallet not found on blockchain. Please verify you have sent coins to your wallet to activate it. Then try your subscription again"
                
            else:
                self.message = "gRPC Error!"
            return
                
        try:        
            subscriptions = sdk.subscriptions.QuerySubscriptionsForAccount(ADDRESS, pagination=PageRequest(limit=1000))
        except (mospy.exceptions.clients.TransactionTimeout,
                mospy.exceptions.clients.NodeException,
                mospy.exceptions.clients.NodeTimeoutException) as e:
            print(str(e))
            self.message = "Error connecting to gRPC. Try again or switch gRPCs"
            return
            
            

        # TODO: Casting all to str is required?
        SubsNodesInfo = [{
            'Denom': "",  # TODO: (?)
            'Deposit': f"{subscription.deposit.amount}{subscription.deposit.denom}",
            'Gigabytes': f"{subscription.gigabytes}",
            'Hours': f"{subscription.hours}",
            'ID': f"{subscription.base.id}",
            'Inactive Date': datetime.fromtimestamp(subscription.base.inactive_at.seconds).strftime('%Y-%m-%d %H:%M:%S.%f'), # '2024-03-26 19:37:52.52297981',
            'Node': subscription.node_address,
            'Owner': subscription.base.address,
            'Plan': '0',  # TODO: (?)
            'Status': ["unspecified", "active", "inactive_pending", "inactive"][subscription.base.status],
        } for subscription in subscriptions]

        # A Dictionary of Lists
        SubsResult = collections.defaultdict(list)

        # Create IBC Denoms
        for d in SubsNodesInfo:
            for k, v in d.items():
                v = self.return_denom(v)
                SubsResult[k].append(v.lstrip().rstrip())

        k=0
        #print(SubsResult)
        for snaddress in SubsResult[NodeKeys.SubsInfoKeys[4]]:
            try:
                if snaddress:
                    NodeData = self.NodeTree.get_node(snaddress).data
                else:
                    k += 1
                    continue
                
                if NodeData is None:
                    raise AttributeError
            except AttributeError:
                SubsFinalResult.append({
                                            NodeKeys.FinalSubsKeys[0] : SubsResult[NodeKeys.SubsInfoKeys[0]][k],
                                            NodeKeys.FinalSubsKeys[1] : "Offline",
                                            NodeKeys.FinalSubsKeys[2] : SubsResult[NodeKeys.SubsInfoKeys[4]][k],
                                            NodeKeys.FinalSubsKeys[3] : SubsResult[NodeKeys.SubsInfoKeys[5]][k],
                                            NodeKeys.FinalSubsKeys[4] : SubsResult[NodeKeys.SubsInfoKeys[7]][k],
                                            NodeKeys.FinalSubsKeys[5] : "",
                                            NodeKeys.FinalSubsKeys[6] : "0.00GB",
                                            NodeKeys.FinalSubsKeys[7] : "0.00B",
                                            NodeKeys.FinalSubsKeys[8] : "None",
                                            NodeKeys.FinalSubsKeys[9] : SubsResult[NodeKeys.SubsInfoKeys[2]][k],
                                            NodeKeys.FinalSubsKeys[10]: SubsResult[NodeKeys.SubsInfoKeys[6]][k]
                                            })
                print("Sub not found in list")
                k += 1
                continue

            if int(SubsResult[NodeKeys.SubsInfoKeys[6]][k]) > 0:
                SubsResult[NodeKeys.SubsInfoKeys[2]][k],nodeQuota = self.GetHourAllocation(SubsResult[NodeKeys.SubsInfoKeys[6]][k], SubsResult[NodeKeys.SubsInfoKeys[2]][k])

            else:
                nodeQuota = self.GetQuota(SubsResult[NodeKeys.SubsInfoKeys[0]][k])
            print(nodeQuota)
            if nodeQuota:
                SubsFinalResult.append({
                                            NodeKeys.FinalSubsKeys[0] : SubsResult[NodeKeys.SubsInfoKeys[0]][k],
                                            NodeKeys.FinalSubsKeys[1] : NodeData[NodeKeys.NodesInfoKeys[0]],
                                            NodeKeys.FinalSubsKeys[2] : SubsResult[NodeKeys.SubsInfoKeys[4]][k],
                                            NodeKeys.FinalSubsKeys[3] : SubsResult[NodeKeys.SubsInfoKeys[5]][k],
                                            NodeKeys.FinalSubsKeys[4] : SubsResult[NodeKeys.SubsInfoKeys[7]][k],
                                            NodeKeys.FinalSubsKeys[5] : NodeData[NodeKeys.NodesInfoKeys[4]],
                                            NodeKeys.FinalSubsKeys[6] : nodeQuota[0],
                                            NodeKeys.FinalSubsKeys[7] : nodeQuota[1],
                                            NodeKeys.FinalSubsKeys[8] : NodeData[NodeKeys.NodesInfoKeys[13]],
                                            NodeKeys.FinalSubsKeys[9] : SubsResult[NodeKeys.SubsInfoKeys[2]][k],
                                            NodeKeys.FinalSubsKeys[10]: SubsResult[NodeKeys.SubsInfoKeys[6]][k]
                                            })
            k += 1

        self.SubResult = deepcopy(SubsFinalResult)


    def GetQuota(self, id):
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)
        grpcaddr, grpcport = self.GRPC.split(":")
        
        try:
            sdk = SDKInstance(grpcaddr, int(grpcport), ssl=True)
        except grpc._channel._InactiveRpcError as e:
            status_code = e.code()
            
            if status_code == StatusCode.NOT_FOUND:
                self.message = "Wallet not found on blockchain. Please verify you have sent coins to your wallet to activate it. Then try your subscription again"
                
            else:
                self.message = "gRPC Error!"
            return
        
        try:
            allocations = sdk.subscriptions.QueryAllocations(subscription_id=int(id))
        except (mospy.exceptions.clients.TransactionTimeout,
                mospy.exceptions.clients.NodeException,
                mospy.exceptions.clients.NodeTimeoutException) as e:
            print(str(e))
            self.message = "Error connecting to gRPC. Try again or switch gRPCs"
            return
        #print(allocations)

        for allocation in allocations:
            if int(allocation.granted_bytes) == int(allocation.utilised_bytes):
                return None
            return [helpers.format_byte_size(int(allocation.granted_bytes), binary_system=False), helpers.format_byte_size(int(allocation.utilised_bytes), binary_system=False)]

                
    def GetHourAllocation(self, hours, idate):
        print(f"Hours: {hours}, inactive_date: {idate}")
        nodeQuota       = []
        nodeQuota.append(str(hours) + "hrs")
        inactive_date   = idate.lstrip().rstrip().split('.')[0]
        inactive_date   = datetime.strptime(inactive_date, '%Y-%m-%d %H:%M:%S')
        ts              = time.time()
        #utc_offset      = float((datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds()/3600)
        #inactive_date   = inactive_date + timedelta(hours=utc_offset)
        now             = datetime.now()
        subdelta        = inactive_date - now
        remaining_hours = round(float(subdelta.total_seconds())/3600,3)
        consumed        = float(int(hours) - remaining_hours)
        if consumed < 0:
            consumed = 0
        if remaining_hours <= 0:
            return None
        else:
            print(f"inactive_date: {str(inactive_date)}, time_remaining: {remaining_hours}, time_consumed: {consumed}")
            nodeQuota.append(str(round(consumed,2)) + "hrs")
            return str(inactive_date),nodeQuota   
                 
def disconnect(v2ray):
    if v2ray:
        try:
            V2Ray = V2RayHandler(v2ray_tun2routes_connect_bash + " down")
            rc = V2Ray.kill_daemon()
            return rc, False
        except Exception as e:
            print(str(e))
            return 1, True
    else:
        CONFFILE = path.join(ConfParams.KEYRINGDIR, 'wg99.conf')
        wg_downCMD = ['pkexec', 'env', 'PATH=%s' % ConfParams.PATH, 'wg-quick', 'down', CONFFILE]
            
        proc1 = Popen(wg_downCMD)
        proc1.wait(timeout=30)
    
        proc_out,proc_err = proc1.communicate()
        return proc1.returncode, False

    