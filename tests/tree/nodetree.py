from subprocess import Popen, PIPE, STDOUT
import collections
from os import path
import re
import requests
import asyncio 
from urllib3.exceptions import InsecureRequestWarning
import pexpect

from treelib import Node, Tree

from continents import OurWorld


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

class NodeTreeData():

    def GetSentinelNodes(self, dt):
        print("Getting Nodes...")
        global ConNodes
        global NodesDictList
        ConNodes,NodesDictList = self.get_nodes()
        print("Nodes begotten and not made")
        
    def get_nodes(self):
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
        
        result = collections.defaultdict(list)
        
        NodeTree = self.CreateNodeTreeStructure(self)
        
        AllNodesSortedStripped = []
        for d in AllNodesInfoSorted:
            for key in NodesInfoKeys:
                d[key] = d[key].lstrip().rstrip()
            AllNodesSortedStripped.append(d)
        
        for d in AllNodesSortedStripped:
            
            d[NodesInfoKeys[3]] = self.return_denom(self, d[NodesInfoKeys[3]])
            
            if "Czechia" in d[NodesInfoKeys[4]]:
                d[NodesInfoKeys[4]] = "Czech Republic"
           
            d_continent = OurWorld.our_world.get_country_continent_name(d[NodesInfoKeys[4]])
            try:
                NodeTree.create_node(d[NodesInfoKeys[4]],d[NodesInfoKeys[4]], parent=d_continent)
            except:
                pass
            try:
                NodeTree.create_node(d[NodesInfoKeys[1]], d[NodesInfoKeys[1]],parent=d[NodesInfoKeys[4]], data=d )
            except:
                pass
        NodeTree.show()
        NodeTree.save2file("nodedata.txt")
        print(NodeTree.get_node("sentnode1w25tyg0ghmsdzcuufep3lfxe6t8puv89jftr3s").data)
        for node in NodeTree.children(OurWorld.CONTINENTS[0]):
            print(node.tag)
            print(len(NodeTree.children(node.tag)))
        print(len(NodeTree.children(OurWorld.CONTINENTS[0])))
        '''    
        #d["City"] = get_city_of_node(d[NodesInfoKeys[1]])
        AllNodesInfoSorted2.append(d)
            
        for d in AllNodesInfoSorted:
            for k, v in d.items():
                v=self.return_denom(v)
                result[k].append(v.lstrip().rstrip())
                
        
    
        return AllNodesInfoSorted2, result
        '''
            
        return NodeTree
    
    def CreateNodeTreeStructure(self):
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

if __name__ == "__main__":
    NodeTreeData.get_nodes(NodeTreeData)