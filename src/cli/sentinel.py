from subprocess import Popen, PIPE, STDOUT
import collections
from os import path, environ
import re
import requests
from urllib3.exceptions import InsecureRequestWarning

from conf.meile_config import MeileGuiConfig

from treelib import  Tree
from geography.continents import OurWorld


# IBC Tokens
IBCSCRT  = 'ibc/31FEE1A2A9F9C01113F90BD0BBCCE8FD6BBB8585FAF109A2101827DD1D5B95B8'
IBCATOM  = 'ibc/A8C2D23A1E6F95DA4E48BA349667E322BD7A6C996D8A4AAE8BA72E190F3D1477'
IBCDEC   = 'ibc/B1C0DDB14F25279A2026BC8794E12B259F8BDA546A3C5132CCAEE4431CE36783'
IBCOSMO  = 'ibc/ED07A3391A112B175915CD8FAF43A2DA8E4790EDE12566649D0C2F97716B8518'
IBCUNKWN = 'ibc/9BCB27203424535B6230D594553F1659C77EC173E36D9CF4759E7186EE747E84'

IBCCOINS = [{'uscrt' : IBCSCRT}, {'uatom' : IBCATOM}, {'udec' : IBCDEC}, {'uosmo' : IBCOSMO}, {'uknwn' :IBCUNKWN}]

SATOSHI = 1000000

USER = environ['SUDO_USER'] if 'SUDO_USER' in environ else environ['USER']
PATH = environ['PATH']
KEYRINGDIR = path.join(path.expanduser('~' + USER), '.meile-gui')
BASEDIR  = path.join(path.expanduser('~' + USER), '.sentinelcli')

APIURL   = "https://api.sentinel.mathnodes.com"

NodesInfoKeys = ["Moniker","Address","Provider","Price","Country","Speed","Latency","Peers","Handshake","Version","Status"]
SubsInfoKeys = ["ID", "Owner", "Plan", "Expiry", "Denom", "Node", "Price", "Deposit", "Free", "Status"]
FinalSubsKeys = [SubsInfoKeys[0], NodesInfoKeys[0],SubsInfoKeys[5], SubsInfoKeys[6], SubsInfoKeys[7], NodesInfoKeys[4], "Allocated", "Consumed" ]

dash = "-"

MeileConfig = MeileGuiConfig()
sentinelcli = MeileConfig.resource_path("../bin/sentinelcli")

class NodeTreeData():
    NodeTree = None
    
    def __init__(self, node_tree):
        if not node_tree:
            self.NodeTree = Tree()
        else:
            self.NodeTree = node_tree
            
   
    def get_nodes(self, latency, *kwargs):
        AllNodesInfo = []
        print("Running sentinel-cli with latency: %s" % latency)
        nodeCMD = [sentinelcli, "query", "nodes", "--node", "https://rpc.mathnodes.com:443", "--limit", "20000", "--timeout", "%s" % latency]
    
        proc = Popen(nodeCMD, stdout=PIPE)
        
        k=1
        
        
        for line in proc.stdout.readlines():
            #print(line)
            if k < 4:  
                k += 1 
                continue
            if k >=4 and '+-------+' in str(line.decode('utf-8')):
                break
            elif "freak12techno" in str(line.decode('utf-8')):
                ninfos = []
                ninfos.append(str(line.decode('utf-8')).split('|')[1])
                for ninf in str(line.decode('utf-8')).split('|')[3:-1]:
                    ninfos.append(ninf)
                AllNodesInfo.append(dict(zip(NodesInfoKeys, ninfos)))
            elif "Testserver" in str(line.decode('utf-8')):
                continue
            else: 
                ninfos = str(line.decode('utf-8')).split('|')[1:-1]
                if ninfos[0].isspace():
                    continue
                elif ninfos[1].isspace():
                    continue
                else:
                    AllNodesInfo.append(dict(zip(NodesInfoKeys, ninfos)))
                #print(ninfos, end='\n')
        
        #get = input("Blah: ")
        AllNodesInfoSorted = sorted(AllNodesInfo, key=lambda d: d[NodesInfoKeys[4]])
        
        #result = collections.defaultdict(list)
        
        self.NodeTree = self.CreateNodeTreeStructure()
        
        for d in AllNodesInfoSorted:
            for key in NodesInfoKeys:
                d[key] = d[key].lstrip().rstrip()
            version = d[NodesInfoKeys[9]].replace('.','')
            if version not in ('030', '031', '032'):
                continue
            d[NodesInfoKeys[3]] = self.return_denom(d[NodesInfoKeys[3]])
            
            if "Czechia" in d[NodesInfoKeys[4]]:
                d[NodesInfoKeys[4]] = "Czech Republic"
           
            d_continent = OurWorld.our_world.get_country_continent_name(d[NodesInfoKeys[4]])
            try:
                self.NodeTree.create_node(d[NodesInfoKeys[4]],d[NodesInfoKeys[4]], parent=d_continent)
            except:
                pass
            try:
                self.NodeTree.create_node(d[NodesInfoKeys[1]], d[NodesInfoKeys[1]],parent=d[NodesInfoKeys[4]], data=d )
            except:
                pass
            
        self.NodeTree.show()
    
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
        for ibc_coin in IBCCOINS:
            for denom,ibc in ibc_coin.items():
                if ibc in tokens:
                    tokens = tokens.replace(ibc, denom)
        
    
        return tokens
    def get_subscriptions(self, ADDRESS):
        SubsNodesInfo = []
        SubsFinalResult    = []
        print("Geting Subscriptions... %s" % ADDRESS)
        subsCMD = [sentinelcli, "query", "subscriptions", "--node", "https://rpc.mathnodes.com:4444", "--status", "Active", "--limit", "100", "--address" ,ADDRESS]
        proc = Popen(subsCMD, stdout=PIPE)
    
        k=1
        for line in proc.stdout.readlines():
            if k < 4:
                k += 1 
                continue
            else: 
                ninfos = str(line.decode('utf-8')).lstrip().rstrip().split('|')[1:-1]
                # List of Dictionaries
                SubsNodesInfo.append(dict(zip(SubsInfoKeys, ninfos)))
        
        # A Dictionary of Lists
        SubsResult = collections.defaultdict(list)
        
        # Create IBC Denoms
        for d in SubsNodesInfo:
            for k, v in d.items():
                v = self.return_denom(v)
                SubsResult[k].append(v.lstrip().rstrip())
                
        k=0
        for snaddress in SubsResult[SubsInfoKeys[5]]:
            try:
                NodeData = self.NodeTree.get_node(snaddress).data
            except AttributeError:
                SubsFinalResult.append({
                                            FinalSubsKeys[0] : SubsResult[SubsInfoKeys[0]][k],
                                            FinalSubsKeys[1] : "Offline",
                                            FinalSubsKeys[2] : SubsResult[SubsInfoKeys[5]][k],
                                            FinalSubsKeys[3] : SubsResult[SubsInfoKeys[6]][k],
                                            FinalSubsKeys[4] : SubsResult[SubsInfoKeys[7]][k],
                                            FinalSubsKeys[5] : None,
                                            FinalSubsKeys[6] : "0B",
                                            FinalSubsKeys[7] : "0B"
                                            })
                print("Sub not found in list")
                k += 1
                continue   
            quotaCMD = [sentinelcli, 'query', 'quotas', '--node', 'https://rpc.mathnodes.com:443', '--page', '1', SubsResult[SubsInfoKeys[0]][k]]
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
                        break
                    else:
                        
                            
                        SubsFinalResult.append({
                                            FinalSubsKeys[0] : SubsResult[SubsInfoKeys[0]][k],
                                            FinalSubsKeys[1] : NodeData[NodesInfoKeys[0]],
                                            FinalSubsKeys[2] : SubsResult[SubsInfoKeys[5]][k],
                                            FinalSubsKeys[3] : SubsResult[SubsInfoKeys[6]][k],
                                            FinalSubsKeys[4] : SubsResult[SubsInfoKeys[7]][k],
                                            FinalSubsKeys[5] : NodeData[NodesInfoKeys[4]],
                                            FinalSubsKeys[6] : nodeQuota[0],
                                            FinalSubsKeys[7] : nodeQuota[1]
                                            })
           
            k += 1 

        return SubsFinalResult



def get_node_infos(naddress):
    endpoint = "/nodes/" + naddress
    
    NodeInfoDict = {}
    
    r = requests.get(APIURL + endpoint)
    
    remote_url = r.json()['result']['node']['remote_url']
    
    

def disconnect():
    #ifCMD = ["ifconfig", "-a"]
    #ifgrepCMD = ["grep", "-oE", "wg[0-9]+"]
    partCMD = ['pkexec', 'env', 'PATH=%s' % PATH, sentinelcli, '--home', BASEDIR, "disconnect"]
    
    #ifoutput = Popen(ifCMD,stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    #grepoutput = Popen(ifgrepCMD, stdin=ifoutput.stdout, stdout=PIPE, stderr=STDOUT)
    #wgif = grepoutput.communicate()[0]
    #wgif_file = str(wgif.decode('utf-8')).replace("\n", '') + ".conf"

    #CONFFILE = path.join(BASEDIR, wgif_file)
    #wg_downCMD = ['wg-quick', 'down', CONFFILE]
        
    proc1 = Popen(partCMD)
    proc1.wait(timeout=10)
    
    #proc = Popen(wg_downCMD, stdout=PIPE, stderr=PIPE)
    #proc_out,proc_err = proc.communicate()
    
    return proc1.returncode, False


    