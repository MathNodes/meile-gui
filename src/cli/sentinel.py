from subprocess import Popen, PIPE, STDOUT
import collections
from os import path
import re
import requests
from urllib3.exceptions import InsecureRequestWarning
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime,timedelta
import time

from treelib import  Tree

from geography.continents import OurWorld
from conf.meile_config import MeileGuiConfig
from typedef.konstants import ConfParams, HTTParams, IBCTokens, TextStrings, NodeKeys
from adapters import HTTPRequests
from cli.v2ray import V2RayHandler
from dns.rdataclass import NONE


MeileConfig = MeileGuiConfig()
sentinelcli = MeileConfig.resource_path("../bin/sentinelcli")
v2ray_tun2routes_connect_bash = MeileConfig.resource_path("../bin/routes.sh")

class NodeTreeData():
    NodeTree      = None
    NodeScores    = {}
    NodeLocations = {}
    NodeTypes     = {}
    
    def __init__(self, node_tree):
        if not node_tree:
            self.NodeTree = Tree()
        else:
            self.NodeTree = node_tree
            
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
            
   
    def get_nodes(self, latency, *kwargs):
        AllNodesInfo = []
        print("Running sentinel-cli with latency: %s" % latency)
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        nodeCMD = [sentinelcli, "query", "nodes", "--node", self.RPC, "--limit", "20000", "--timeout", "%s" % latency]
    
        proc = Popen(nodeCMD, stdout=PIPE)
        
        k=1
        
        
        for line in proc.stdout.readlines():
            line = str(line.decode('utf-8'))
            if k < 4:  
                k += 1 
                continue
            if k >=4 and '+-------+' in line:
                break
            elif "freak12techno" in line:
                ninfos = []
                ninfos.append(line.split('|')[1])
                for ninf in line.split('|')[3:-1]:
                    ninfos.append(ninf)
                AllNodesInfo.append(dict(zip(NodeKeys.NodesInfoKeys, ninfos)))
            elif "Testserver" in line:
                continue
            else: 
                ninfos = line.split('|')[1:-1]
                if ninfos[0].isspace():
                    continue
                elif ninfos[1].isspace():
                    continue
                else:
                    AllNodesInfo.append(dict(zip(NodeKeys.NodesInfoKeys, ninfos)))
        
        AllNodesInfoSorted = sorted(AllNodesInfo, key=lambda d: d[NodeKeys.NodesInfoKeys[4]])
        
        #result = collections.defaultdict(list)
        
        self.NodeTree = self.CreateNodeTreeStructure()
        
        for d in AllNodesInfoSorted:
            for key in NodeKeys.NodesInfoKeys:
                d[key] = d[key].lstrip().rstrip()
            d[NodeKeys.NodesInfoKeys[10]] = d[NodeKeys.NodesInfoKeys[10]].split('-')[0]
            version = d[NodeKeys.NodesInfoKeys[10]].replace('.','')
            if version not in NodeKeys.NodeVersions:
                continue
            
            # Gigabyte Prices
            d[NodeKeys.NodesInfoKeys[2]] = self.return_denom(d[NodeKeys.NodesInfoKeys[2]])
            d[NodeKeys.NodesInfoKeys[2]] = self.parse_coin_deposit(d[NodeKeys.NodesInfoKeys[2]])
            
            # Hourly Prices
            d[NodeKeys.NodesInfoKeys[3]] = self.return_denom(d[NodeKeys.NodesInfoKeys[3]])
            d[NodeKeys.NodesInfoKeys[3]] = self.parse_coin_deposit(d[NodeKeys.NodesInfoKeys[3]])
            
            
            if  OurWorld.CZ in d[NodeKeys.NodesInfoKeys[4]]:
                d[NodeKeys.NodesInfoKeys[4]] = OurWorld.CZ_FULL
           
            d_continent = OurWorld.our_world.get_country_continent_name(d[NodeKeys.NodesInfoKeys[4]])
            try:
                self.NodeTree.create_node(d[NodeKeys.NodesInfoKeys[4]],d[NodeKeys.NodesInfoKeys[4]], parent=d_continent)
            except:
                pass
            try:
                self.NodeTree.create_node(d[NodeKeys.NodesInfoKeys[1]], d[NodeKeys.NodesInfoKeys[1]],parent=d[NodeKeys.NodesInfoKeys[4]], data=d )
            except:
                pass
            
        self.NodeTree.show()
        self.GetNodeScores()
        self.GetNodeLocations()
        self.GetNodeTypes()
        
    def GetNodeScores(self):
        Request = HTTPRequests.MakeRequest(TIMEOUT=2)
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
        Request = HTTPRequests.MakeRequest(TIMEOUT=2)
        http = Request.hadapter()
        try:
            r = http.get(HTTParams.SERVER_URL + HTTParams.NODE_LOCATION_ENDPOINT)
            data = r.json()
          
            for nlist in data['data']:
                k=0
                self.NodeLocations[nlist[k]] = nlist[k+1]
            
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
    
    def CreateNodeTreeStructure(self, **kwargs):
        NodeTreeBase = Tree()
        RootTag = "CONTINENTS"
        RootIdentifier = RootTag.lower()
        NodeTreeBase.create_node(RootTag, RootIdentifier)
        
        for c in OurWorld.CONTINENTS:
            NodeTreeBase.create_node(c, c, parent=RootIdentifier)
            
        NodeTreeBase.show()
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
        subsCMD = [sentinelcli, "query", "subscriptions", "--node", self.RPC, "--limit", "1000", "--address" ,ADDRESS]
        proc = Popen(subsCMD, stdout=PIPE)
    
        k=1
        for line in proc.stdout.readlines():
            if k < 4:
                k += 1 
                continue
            elif k % 2 == 0: 
                ninfos = str(line.decode('utf-8')).lstrip().rstrip().split('|')[1:-1]
                # List of Dictionaries
                SubsNodesInfo.append(dict(zip(NodeKeys.SubsInfoKeys, ninfos)))
                k += 1
            else:
                k += 1
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
                                            NodeKeys.FinalSubsKeys[5] : None,
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
                                            NodeKeys.FinalSubsKeys[8] : NodeData[NodeKeys.NodesInfoKeys[9]],
                                            NodeKeys.FinalSubsKeys[9] : SubsResult[NodeKeys.SubsInfoKeys[2]][k],
                                            NodeKeys.FinalSubsKeys[10]: SubsResult[NodeKeys.SubsInfoKeys[6]][k]
                                            })
            k += 1 

        return SubsFinalResult   


    def GetQuota(self, id):
        CONFIG = MeileConfig.read_configuration(MeileConfig.CONFFILE)
        self.RPC = CONFIG['network'].get('rpc', HTTParams.RPC)
        quotaCMD = [sentinelcli, 'query', 'allocations', '--node', self.RPC, '--page', '1', id]
        proc = Popen(quotaCMD, stdout=PIPE)
        h=1
        for line in proc.stdout.readlines():
            if h < 4:
                h += 1 
                continue
            if h >=4 and '+-----------+' in str(line.decode('utf-8')):
                break
            else:
                nodeQuota = str(line.decode('utf-8')).split("|")[2:-1]
                allotted = float(re.findall(r'[0-9]+\.[0-9]+', nodeQuota[0])[0])
                consumed = float(re.findall(r'[0-9]+\.[0-9]+', nodeQuota[1])[0])
                
                if allotted == consumed:
                    return None
                else:
                    return nodeQuota
                
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

    