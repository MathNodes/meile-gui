from subprocess import Popen, PIPE, STDOUT
import collections
from os import path
import re
import requests
from urllib3.exceptions import InsecureRequestWarning
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime,timedelta
import time
from urllib.parse import urlparse

from treelib import  Tree
from treelib.exceptions import DuplicatedNodeIdError

from geography.continents import OurWorld
from conf.meile_config import MeileGuiConfig
from typedef.konstants import ConfParams, HTTParams, IBCTokens, TextStrings, NodeKeys
from adapters import HTTPRequests
from cli.v2ray import V2RayHandler
from helpers import helpers

from sentinel_sdk.sdk import SDKInstance
from sentinel_sdk.types import PageRequest, Status

MeileConfig = MeileGuiConfig()
sentinelcli = MeileConfig.resource_path("../bin/sentinelcli")
v2ray_tun2routes_connect_bash = MeileConfig.resource_path("../bin/routes.sh")

class NodeTreeData():
    NodeTree      = None
    NodeScores    = {}
    NodeLocations = {}
    NodeTypes     = {}
    NodeHealth    = {}
    NodeFormula   = {}
    
    def __init__(self, node_tree):
        if not node_tree:
            self.NodeTree = Tree()
        else:
            self.NodeTree = node_tree
            
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        
    def get_nodes(self, latency, *kwargs):
        AllNodesInfo = []
        ninfos       = []
        
        
        # Use Cache Server for faster loading.  
        Request = HTTPRequests.MakeRequest(TIMEOUT=23) # long timeout in case there is heavy load
        http = Request.hadapter()
        try:
            r = http.get(HTTParams.NODE_API) 
            data = r.json()
            #rint(data)
            for node in data:
                ninfos.append(node['Moniker'])
                ninfos.append(node['Node Address'])
                ninfos.append(node['Gigabyte Prices'])
                ninfos.append(node['Hourly Prices'])
                if "The Netherlands" in node['Country']:
                    node['Country'] = "Netherlands"
                elif "Czech Republic" in node['Country']:
                    node['Country'] = "Czechia"
                ninfos.append(node['Country'])
                ninfos.append(node['City'])
                ninfos.append(node['Latitude'])
                ninfos.append(node['Longitude'])
                ninfos.append(node['Bandwidth Down'])
                ninfos.append(node['Bandwidth Up'])
                ninfos.append(node['Connected Peers'])
                ninfos.append(node['Max Peers'])
                ninfos.append(node['Handshake'])
                ninfos.append("WireGuard" if node['Node Type'] == 1 else "V2Ray")
                ninfos.append(node['Node Version'])
                AllNodesInfo.append(dict(zip(NodeKeys.NodesInfoKeys, ninfos)))
                ninfos.clear()
                
        except Exception as e:
            print(str(e))
            pass
        
        AllNodesInfoSorted = sorted(AllNodesInfo, key=lambda d: d[NodeKeys.NodesInfoKeys[4]])
        
        self.NodeTree = self.CreateNodeTreeStructure(data)
        
        #print(AllNodesInfoSorted)
        
        for d in AllNodesInfoSorted:
            
            '''Parse out old node versions < 0.7.0'''   
            
            d[NodeKeys.NodesInfoKeys[14]] = d[NodeKeys.NodesInfoKeys[14]].split('-')[0]
            version = d[NodeKeys.NodesInfoKeys[14]].replace('.','')
            if version not in NodeKeys.NodeVersions:
                continue
            
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
            
        # For pretty output. Unicode is used in treelib > 1.6.1     
        self.NodeTree.show()
        # User-submitted Ratings
        self.GetNodeScores()
        # Hosting, Residential, etc
        self.GetNodeTypes()
        # Sentinel Health Check Results
        # Will process Health Check on-the-fly in NodeScreen. 
        # Not loading all the data here is a 2x improvement on loadtime
        #self.GetHealthCheckData()

        # Get MathNodes NodeFormula
        self.GetNodeFormula()

    def GetHealthCheckData(self):
        Request = HTTPRequests.MakeRequest(TIMEOUT=4)
        http = Request.hadapter()
        try:
            r = http.get(HTTParams.HEALTH_CHECK) #specify a constant in konstants.py
            data = r.json()

            for nodehealthdata in data['result']:
                # integrity check
                if nodehealthdata['status'] != 1:
                    self.NodeHealth[nodehealthdata['addr']] = False
                elif "info_fetch_error " in nodehealthdata:
                    self.NodeHealth[nodehealthdata['addr']] = False
                elif "config_exchange_error" in nodehealthdata:
                    self.NodeHealth[nodehealthdata['addr']] = False
                elif "location_fetch_error" in nodehealthdata:
                    self.NodeHealth[nodehealthdata['addr']] = False
                else:
                    self.NodeHealth[nodehealthdata['addr']] = True


        except Exception as e:
            print(str(e))
        
    def GetNodeScores(self):
        Request = HTTPRequests.MakeRequest(TIMEOUT=4)
        http = Request.hadapter()
        try:
            r = http.get(HTTParams.SERVER_URL + HTTParams.NODE_SCORE_ENDPOINT)
            data = r.json()
          
            for nlist in data['data']:
                k=0
                self.NodeScores[nlist[k]] = [nlist[k+1], nlist[k+2]]
        except Exception as e:
            print(str(e)) 
            
    def GetNodeLocations(self):
        Request = HTTPRequests.MakeRequest(TIMEOUT=4)
        http = Request.hadapter()
        try:
            r = http.get(HTTParams.SERVER_URL + HTTParams.NODE_LOCATION_ENDPOINT)
            data = r.json()
          
            for nlist in data['data']:
                k=0
                self.NodeLocations[nlist[k]] = nlist[k+1]
            
        except Exception as e:
            print(str(e)) 
    
    def GetNodeFormula(self):
        Request = HTTPRequests.MakeRequest(TIMEOUT=4)
        http = Request.hadapter()
        try:
            r = http.get(HTTParams.SERVER_URL + HTTParams.NODE_FORMULA_ENDPOINT)
            data = r.json()
          
            for nlist in data['data']:
                #k=0
                self.NodeFormula[nlist[0]] = nlist[6]
            
        except Exception as e:
            print(str(e)) 
            
    def GetNodeTypes(self):
        Request = HTTPRequests.MakeRequest(TIMEOUT=2)
        http = Request.hadapter()
        try:
            r = http.get(HTTParams.SERVER_URL + HTTParams.NODE_TYPE_ENDPOINT)
            data = r.json()

            for nlist in data['data']:
                k=0
                self.NodeTypes[nlist[k]] = nlist[k+3]

        except Exception as e:
            print(str(e))
    
    def CreateNodeTreeStructure(self, data, **kwargs):
        NodeTreeBase = Tree()
        RootTag = "SENTINEL"
        RootIdentifier = RootTag.lower()
        NodeTreeBase.create_node(RootTag, RootIdentifier)
        
        for node in data:
            if "The Netherlands" in node['Country']:
                node['Country'] = "Netherlands"
            elif "Czech Republic" in node['Country']:
                node['Country'] = "Czechia"
            
            c = node['Country']
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
        
        grpcaddr, grpcport = urlparse(self.GRPC).netloc.split(":")
        sdk = SDKInstance(grpcaddr, int(grpcport))
        subscriptions = sdk.subscriptions.QuerySubscriptionsForAccount(ADDRESS, pagination=PageRequest(limit=1000))

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
                NodeData = self.NodeTree.get_node(snaddress).data
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

        return SubsFinalResult


    def GetQuota(self, id):
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)

        self.GRPC = CONFIG['network'].get('grpc', HTTParams.GRPC)
        
        grpcaddr, grpcport = urlparse(self.GRPC).netloc.split(":")
        sdk = SDKInstance(grpcaddr, int(grpcport))
        allocations = sdk.subscriptions.QueryAllocations(subscription_id=int(id))

        for allocation in allocations:
            if int(allocation.granted_bytes) == int(allocation.utilised_bytes):
                return None
            return [helpers.format_byte_size(int(allocation.granted_bytes), binary_system=False), helpers.format_byte_size(int(allocation.utilised_bytes), binary_system=False)]

                
    def GetHourAllocation(self, hours, idate):
        nodeQuota       = []
        nodeQuota.append(str(hours) + "hrs")
        inactive_date   = idate.lstrip().rstrip().split('.')[0]
        inactive_date   = datetime.strptime(inactive_date, '%Y-%m-%d %H:%M:%S')
        ts              = time.time()
        utc_offset      = float((datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds()/3600)
        inactive_date   = inactive_date + timedelta(hours=utc_offset)
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
        CONFFILE = path.join(ConfParams.BASEDIR, 'wg99.conf')
        wg_downCMD = ['pkexec', 'env', 'PATH=%s' % ConfParams.PATH, 'wg-quick', 'down', CONFFILE]
            
        proc1 = Popen(wg_downCMD)
        proc1.wait(timeout=30)
    
        proc_out,proc_err = proc1.communicate()
        return proc1.returncode, False

    