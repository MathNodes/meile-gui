from subprocess import Popen, PIPE, STDOUT
import collections
from os import path
import re
import requests
from urllib3.exceptions import InsecureRequestWarning

from conf.meile_config import MeileGuiConfig

from treelib import  Tree
from geography.continents import OurWorld

from typedef.konstants import ConfParams 
from typedef.konstants import HTTParams
from typedef.konstants import IBCTokens
from typedef.konstants import TextStrings
from typedef.konstants import NodeKeys
from adapters import HTTPRequests


MeileConfig = MeileGuiConfig()
sentinelcli = MeileConfig.resource_path("../bin/sentinelcli")


class NodeTreeData():
    NodeTree = None
    NodeScores = {}
    NodeLocations = {}
    
    def __init__(self, node_tree):
        if not node_tree:
            self.NodeTree = Tree()
        else:
            self.NodeTree = node_tree
            
   
    def get_nodes(self, latency, *kwargs):
        AllNodesInfo = []
        print("Running sentinel-cli with latency: %s" % latency)
        nodeCMD = [sentinelcli, "query", "nodes", "--node", HTTParams.RPC, "--limit", "20000", "--timeout", "%s" % latency]
    
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
            version = d[NodeKeys.NodesInfoKeys[9]].replace('.','')
            if version not in NodeKeys.NodeVersions:
                continue
            d[NodeKeys.NodesInfoKeys[3]] = self.return_denom(d[NodeKeys.NodesInfoKeys[3]])
            
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
        
    def GetNodeScores(self):
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        try:
            r = http.get(HTTParams.SERVER_URL + HTTParams.NODE_SCORE_ENDPOINT)
            data = r.json()
          
            for nlist in data['data']:
                k=0
                self.NodeScores[nlist[k]] = [nlist[k+1], nlist[k+2]]
            #print(self.NodeScores)
        except Exception as e:
            print(str(e)) 
            
    def GetNodeLocations(self):
        Request = HTTPRequests.MakeRequest()
        http = Request.hadapter()
        try:
            r = http.get(HTTParams.SERVER_URL + HTTParams.NODE_LOCATION_ENDPOINT)
            data = r.json()
          
            for nlist in data['data']:
                k=0
                self.NodeLocations[nlist[k]] = nlist[k+1]
            #print(self.NodeLocations)
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
    def get_subscriptions(self, ADDRESS):
        SubsNodesInfo = []
        SubsFinalResult    = []
        print("Geting Subscriptions... %s" % ADDRESS)
        subsCMD = [sentinelcli, "query", "subscriptions", "--node", HTTParams.RPC, "--status", "Active", "--limit", "100", "--address" ,ADDRESS]
        proc = Popen(subsCMD, stdout=PIPE)
    
        k=1
        for line in proc.stdout.readlines():
            if k < 4:
                k += 1 
                continue
            else: 
                ninfos = str(line.decode('utf-8')).lstrip().rstrip().split('|')[1:-1]
                # List of Dictionaries
                SubsNodesInfo.append(dict(zip(NodeKeys.SubsInfoKeys, ninfos)))
        
        # A Dictionary of Lists
        SubsResult = collections.defaultdict(list)
        
        # Create IBC Denoms
        for d in SubsNodesInfo:
            for k, v in d.items():
                v = self.return_denom(v)
                SubsResult[k].append(v.lstrip().rstrip())
                
        k=0
        for snaddress in SubsResult[NodeKeys.SubsInfoKeys[5]]:
            try:
                NodeData = self.NodeTree.get_node(snaddress).data
            except AttributeError:
                SubsFinalResult.append({
                                            NodeKeys.FinalSubsKeys[0] : SubsResult[NodeKeys.SubsInfoKeys[0]][k],
                                            NodeKeys.FinalSubsKeys[1] : "Offline",
                                            NodeKeys.FinalSubsKeys[2] : SubsResult[NodeKeys.SubsInfoKeys[5]][k],
                                            NodeKeys.FinalSubsKeys[3] : SubsResult[NodeKeys.SubsInfoKeys[6]][k],
                                            NodeKeys.FinalSubsKeys[4] : SubsResult[NodeKeys.SubsInfoKeys[7]][k],
                                            NodeKeys.FinalSubsKeys[5] : None,
                                            NodeKeys.FinalSubsKeys[6] : "0.00GB",
                                            NodeKeys.FinalSubsKeys[7] : "0.00B"
                                            })
                print("Sub not found in list")
                k += 1
                continue
            
            nodeQuota = self.GetQuota(SubsResult[NodeKeys.SubsInfoKeys[0]][k])
            if nodeQuota:
                SubsFinalResult.append({
                                            NodeKeys.FinalSubsKeys[0] : SubsResult[NodeKeys.SubsInfoKeys[0]][k],
                                            NodeKeys.FinalSubsKeys[1] : NodeData[NodeKeys.NodesInfoKeys[0]],
                                            NodeKeys.FinalSubsKeys[2] : SubsResult[NodeKeys.SubsInfoKeys[5]][k],
                                            NodeKeys.FinalSubsKeys[3] : SubsResult[NodeKeys.SubsInfoKeys[6]][k],
                                            NodeKeys.FinalSubsKeys[4] : SubsResult[NodeKeys.SubsInfoKeys[7]][k],
                                            NodeKeys.FinalSubsKeys[5] : NodeData[NodeKeys.NodesInfoKeys[4]],
                                            NodeKeys.FinalSubsKeys[6] : nodeQuota[0],
                                            NodeKeys.FinalSubsKeys[7] : nodeQuota[1]
                                            })
            k += 1 

        return SubsFinalResult   


    def GetQuota(self, id):
        quotaCMD = [sentinelcli, 'query', 'quotas', '--node', HTTParams.RPC, '--page', '1', id]
        proc = Popen(quotaCMD, stdout=PIPE)
        h=1
        for line in proc.stdout.readlines():
            #print(line)
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
                
def disconnect():
    #ifCMD = ["ifconfig", "-a"]
    #ifgrepCMD = ["grep", "-oE", "wg[0-9]+"]
    #partCMD = ['pkexec', 'env', 'PATH=%s' % ConfParams.PATH, sentinelcli, '--home', ConfParams.BASEDIR, "disconnect"]
    #partCMD  = ['pkexec', 'env', 'PATH=%s' % ConfParams.PATH, 'wg-quick', 'down']
    #ifoutput = Popen(ifCMD,stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    #grepoutput = Popen(ifgrepCMD, stdin=ifoutput.stdout, stdout=PIPE, stderr=STDOUT)
    #wgif = grepoutput.communicate()[0]
    #wgif_file = str(wgif.decode('utf-8')).replace("\n", '') + ".conf"

    #CONFFILE = path.join(BASEDIR, wgif_file)
    CONFFILE = path.join(ConfParams.BASEDIR, 'wg99.conf')
    wg_downCMD = ['pkexec', 'env', 'PATH=%s' % ConfParams.PATH, 'wg-quick', 'down', CONFFILE]
        
    proc1 = Popen(wg_downCMD)
    proc1.wait(timeout=30)
    
    #proc = Popen(wg_downCMD, stdout=PIPE, stderr=PIPE)
    #proc_out,proc_err = proc.communicate()
    
    return proc1.returncode, False


    