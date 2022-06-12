from subprocess import Popen, PIPE, STDOUT
import collections
from os import path
import re
import requests

from urllib3.exceptions import InsecureRequestWarning


# IBC Tokens
IBCSCRT  = 'ibc/31FEE1A2A9F9C01113F90BD0BBCCE8FD6BBB8585FAF109A2101827DD1D5B95B8'
IBCATOM  = 'ibc/A8C2D23A1E6F95DA4E48BA349667E322BD7A6C996D8A4AAE8BA72E190F3D1477'
IBCDEC   = 'ibc/B1C0DDB14F25279A2026BC8794E12B259F8BDA546A3C5132CCAEE4431CE36783'
IBCOSMO  = 'ibc/ED07A3391A112B175915CD8FAF43A2DA8E4790EDE12566649D0C2F97716B8518'
IBCUNKWN = 'ibc/9BCB27203424535B6230D594553F1659C77EC173E36D9CF4759E7186EE747E84'

IBCCOINS = [{'uscrt' : IBCSCRT}, {'uatom' : IBCATOM}, {'udec' : IBCDEC}, {'uosmo' : IBCOSMO}, {'uknwn' :IBCUNKWN}]

SATOSHI = 1000000

BASEDIR  = path.join(path.expanduser('~'), '.sentinelcli')
APIURL   = "https://api.sentinel.mathnodes.com"
NodesInfoKeys = ["Moniker","Address","Provider","Price","Country","Speed","Latency","Peers","Handshake","Version","Status"]
SubsInfoKeys = ["ID", "Owner", "Plan", "Expiry", "Denom", "Node", "Price", "Deposit", "Free", "Status"]
FinalSubsKeys = [SubsInfoKeys[0], NodesInfoKeys[0],SubsInfoKeys[5], SubsInfoKeys[6], SubsInfoKeys[7], NodesInfoKeys[4], "Allocated", "Consumed" ]


dash = "-"

global ConNodes
ConNodes = []
global NodesDictList
NodesDictList = collections.defaultdict(list)


def GetSentinelNodes(dt):
    print("Getting Nodes...")
    global ConNodes
    global NodesDictList
    ConNodes,NodesDictList = get_nodes()
    print("Nodes begotten and not made")
    
def get_nodes():
    AllNodesInfo = []
    nodeCMD = ["sentinelcli", "query", "nodes", "--node", "https://rpc.mathnodes.com:4444", "--limit", "20000"]

    proc = Popen(nodeCMD, stdout=PIPE)
    
    k=1
    
    print()
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
    AllNodesInfoSorted2 = []
    result = collections.defaultdict(list)

    for d in AllNodesInfoSorted:
        d[NodesInfoKeys[3]] = return_denom(d[NodesInfoKeys[3]])
        #d["City"] = get_city_of_node(d[NodesInfoKeys[1]])
        AllNodesInfoSorted2.append(d)
        
    for d in AllNodesInfoSorted:
        for k, v in d.items():
            v=return_denom(v)
            result[k].append(v.lstrip().rstrip())
            
    

    return AllNodesInfoSorted2, result

def return_denom(tokens):
    for ibc_coin in IBCCOINS:
        for denom,ibc in ibc_coin.items():
            if ibc in tokens:
                tokens = tokens.replace(ibc, denom)
    

    return tokens

def get_subscriptions(result, ADDRESS):
    SubsNodesInfo = []
    SubsFinalResult    = []
    subsCMD = ["sentinelcli", "query", "subscriptions", "--node", "https://rpc.mathnodes.com:4444", "--status", "Active", "--limit", "100", "--address" ,ADDRESS]
    proc = Popen(subsCMD, stdout=PIPE)

    k=1
    for line in proc.stdout.readlines():
        #print(line)
        if k < 4:
            k += 1 
            continue
        else: 
            ninfos = str(line.decode('utf-8')).lstrip().rstrip().split('|')[1:-1]
            SubsNodesInfo.append(dict(zip(SubsInfoKeys, ninfos)))
            
    SubsResult = collections.defaultdict(list)
    
    for d in SubsNodesInfo:
        for k, v in d.items():
            v = return_denom(v)
            SubsResult[k].append(v.lstrip().rstrip())
            
    SubsAddressSet = set(SubsResult[SubsInfoKeys[5]])
    #NodesAddressSet = set(result[NodesInfoKeys[1]])
    
    # The Index of Subscription Address in All Data
    Nodespos = [i for i,val in enumerate(result[NodesInfoKeys[1]]) if val in SubsAddressSet]
    NodeAddys = [val for i,val in enumerate(result[NodesInfoKeys[1]]) if val in SubsAddressSet]
    
    # Available Subscriptions
    #Subspos = [i for i,val in enumerate(SubsResult[SubsInfoKeys[5]]) if val in NodesAddressSet]
    #SubsAddys = [val for i,val in enumerate(SubsResult[SubsInfoKeys[5]]) if val in NodesAddressSet]
    #print(Subspos)
    #print(SubsResult[SubsInfoKeys[5]])
    
  
    k=0
    j=0
    # This would be the more efficent algorithm. Not a fan of O(n^2)
    #for e1,e2 in zip(Nodespos,Subspos):
    for sub in SubsResult[SubsInfoKeys[5]]:
        for node in NodeAddys:
            if sub == node:
                quotaCMD = ['sentinelcli', 'query', 'quotas', '--node', 'https://rpc.mathnodes.com:4444', '--page', '1', SubsResult[SubsInfoKeys[0]][k]]
        
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
                                                FinalSubsKeys[1] : result[NodesInfoKeys[0]][Nodespos[j]],
                                                FinalSubsKeys[2] : SubsResult[SubsInfoKeys[5]][k],
                                                FinalSubsKeys[3] : SubsResult[SubsInfoKeys[6]][k],
                                                FinalSubsKeys[4] : SubsResult[SubsInfoKeys[7]][k],
                                                FinalSubsKeys[5] : result[NodesInfoKeys[4]][Nodespos[j]],
                                                FinalSubsKeys[6] : nodeQuota[0],
                                                FinalSubsKeys[7] : nodeQuota[1]
                                                })

                break
            else:
                j += 1
                continue
        j=0
        k += 1

     
    return SubsFinalResult

def get_balance(address):
    endpoint = "/bank/balances/" + address
    CoinDict = {}
    r = requests.get(APIURL + endpoint)
    
    coinJSON = r.json()
    
    for coin in coinJSON['result']:
        if "udvpn" in coin['denom']:
            CoinDict['dvpn'] = round(float(float(coin['amount']) / SATOSHI),4)
        elif IBCSCRT in coin['denom']:
            CoinDict['scrt'] = round(float(float(coin['amount']) / SATOSHI),4)
        elif IBCDEC in coin['denom']:
            CoinDict['dec'] = round(float(float(coin['amount']) / SATOSHI),4)
            
    return CoinDict

def get_node_infos(naddress):
    endpoint = "/nodes/" + naddress
    
    NodeInfoDict = {}
    
    r = requests.get(APIURL + endpoint)
    
    remote_url = r.json()['result']['node']['remote_url']
    
    

def disconnect():
    ifCMD = ["ifconfig", "-a"]
    ifgrepCMD = ["grep", "-oE", "wg[0-9]+"]
    partCMD = ["sentinelcli", "disconnect"]
    
    ifoutput = Popen(ifCMD,stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    grepoutput = Popen(ifgrepCMD, stdin=ifoutput.stdout, stdout=PIPE, stderr=STDOUT)
    wgif = grepoutput.communicate()[0]
    wgif_file = str(wgif.decode('utf-8')).replace("\n", '') + ".conf"

    CONFFILE = path.join(BASEDIR, wgif_file)
    wg_downCMD = ['wg-quick', 'down', CONFFILE]
        
    proc1 = Popen(partCMD)
    proc1.wait(timeout=10)
    
    proc = Popen(wg_downCMD, stdout=PIPE, stderr=PIPE)
    proc_out,proc_err = proc.communicate()
    
    return proc.returncode, False

def connect(ID, address, keyname):
    connCMD = ["sentinelcli", "connect", "--keyring-backend", "os", "--chain-id", "sentinelhub-2",
               "--node", "https://rpc.mathnodes.com:4444", "--gas-prices", "0.1udvpn", "--yes", "--from",keyname, ID, address]
    proc = Popen(connCMD, stdout=PIPE, stderr=PIPE)
    proc_out,proc_err = proc.communicate()
    
    if path.isfile(path.join(BASEDIR, "status.json")):
        CONNECTED = True
    else:
        CONNECTED = False
        
    return proc.returncode, CONNECTED

def subscribe(KEYNAME, NODE, DEPOSIT):

    subscribeCMD = ["sentinelcli", "tx", "subscription", "subscribe-to-node", "--home", BASEDIR,  "--yes",
                    "--keyring-backend", "os", "--gas-prices", "0.1udvpn", "--chain-id", "sentinelhub-2",
                    "--node", "https://rpc.mathnodes.com:4444", "--from", "%s" % KEYNAME, NODE, DEPOSIT]
    
    subproc = Popen(subscribeCMD, stdout=PIPE, stderr=PIPE)
    proc_out,proc_err = subproc.communicate()
    #print(proc_out+proc_err)
    return subproc.returncode
    
    
    
    