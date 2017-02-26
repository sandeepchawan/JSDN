from get_link_info import *
import pprint
from link_latency_get import *
import json
import heapq


def shortestPath(start, end,graph):
	queue,seen = [(0, start, [])], set()
	while True:
	    (cost, v, path) = heapq.heappop(queue)
	    if v not in seen:
		path = path + [v]
		seen.add(v)
		if v == end:
		    return {'nhop':path, 'cost':cost}
		for (next, c) in graph[v].iteritems():
		    heapq.heappush(queue, (cost + c, next, path))


original_routers = [
           { 'name': 'Chicago', 'router_id': '10.210.10.124', 'adj': []},
           { 'name': 'SF', 'router_id': '10.210.10.100','adj': []},
           { 'name': 'Dallas', 'router_id': '10.210.10.106','adj': []},
           { 'name': 'Miami', 'router_id': '10.210.10.112','adj': []},
           { 'name': 'NY', 'router_id': '10.210.10.118','adj': []},
           { 'name': 'LA', 'router_id': '10.210.10.113','adj': []},
           { 'name': 'Houston', 'router_id': '10.210.10.114','adj': []},
           { 'name': 'Tampa', 'router_id': '10.210.10.115','adj': []}
           ]
routers = original_routers

def calculateLinkCost(adj):
	#reference bw, default = 1bps link = 10^9
	ref_bw = 1000000000
	bw = adj['bw']
	rtt = adj['rtt']
	reli = adj['reliability']
	#r_prior = adj['r_prior'] 
	
	#Link cost: ((RTT/20  * 256)    +   reference-bw / reservered-min-bw ) * router-priority 
	#priority 1 -> 15, 1 = highest priority = lowest cost
	cost =  ((rtt/20 * 256) + ((ref_bw)/bw)) * reli
	
	return int(cost)


def getRouterAdj(newRouter):
	routers = newRouter
	for router in routers:
		#print "getRouterAdj", router['router_id']
		neighbors = getNodeNeighbors(router['router_id'])
		for neighbor in neighbors:
			neighbor['cost'] = calculateLinkCost(neighbor)

		router['adj'] = neighbors
	return routers
			

#getRouterAdj()
#pprint.pprint(routers)

topoGraph = {}
backupPaths= [] 

def createTopologyGraph(excRouters = []):
	if excRouters:
		newRouters = routers
		for excR in excRouters:
			for router in newRouters:
				if router['router_id'] == excR:
					newRouters.remove(router)
					break
		getRouterAdj(newRouters)
	else:
		getRouterAdj(original_routers)
	for router in routers:
		adjs = {}
		for adj in router['adj']:
			if adj['n_id'] not in excRouters:
				adjs.update({adj['n_id']: adj['cost']})
			
		topoGraph.update({router['router_id']: adjs})
	return topoGraph	
	
#reateTopologyGraph()
#print "Topology Graph"
#pprint.pprint(topoGraph)
	
#curShortestPath = {}
curShortestIPHops = [] 
#shortestPath('10.210.10.118','10.210.10.100', topoGraph)
#print "Best Shortest Path"
#print curShortestPath


def calculateBackupSP(curShortestPath):
	#print curShortestPath
	hops = curShortestPath['nhop']
	i = 0
	
	while i < (len(hops) - 1):
		endA = hops[i]
		endZ = hops[i+1]
		newGraph = topoGraph
		newGraph[endA].pop(endZ, None)
		#pprint.pprint(newGraph)
		newSP = shortestPath(hops[0], hops[-1], newGraph)
		#pprint.pprint(newSP)
		backupPaths.append(newSP)
		i+=1
	backupPaths.sort()
def findNewBackup(hops, downIP1, downIP2):
	newGraph = topoGraph
	i=0
	#pprint.pprint(hops)
	while i < (len(hops) - 1):
                endA = hops[i]
                endZ = hops[i+1]
                newGraph = topoGraph
                newGraph[endA].pop(endZ, None)
		try:
			newGraph[endA].pop(downIP1, None)
			newGraph[endA].pop(downIP2, None)
		except:
			pass
                #pprint.pprint(newGraph)
                newSP = shortestPath(hops[0], hops[-1], newGraph)
                #pprint.pprint(newSP)
                backupPaths.append(newSP)
                i+=1
	backupPaths.sort()

#alculateBackupSP()

def getShortestPath(excRouters = []):
	print "Creating new Topology"
	createTopologyGraph(excRouters)
	#pprint.pprint(topoGraph)
	curShortestPath = shortestPath('10.210.10.100','10.210.10.118', topoGraph)
	#rint "Shortest Path:"
	#print.pprint(curShortestPath)
	
	print "Calculating new Backup Paths\n"
	calculateBackupSP(curShortestPath)
 
	
	ipHops = getHopsIP(curShortestPath['nhop'])
	curShortestIPHops = ipHops
	
	return ipHops, curShortestPath

def getHopsIP(rHops):
	startIP = rHops[0]
	#endIP = routerHops[-1]
	hopsIP = []
	
	#print "Router Hops: " , rHops
	i = 0
	while i < (len(rHops) -1):
		curr = rHops[i]
		nextR = rHops[i+1] 
	
		for router in routers:
			if curr == router['router_id'] and curr == startIP:
				for adj in router['adj']:
					if adj['n_id'] == nextR:
						hopsIP.append(adj['localIP'])
						hopsIP.append(adj['peerIP'])
						break
				break
			elif curr == router['router_id']:
					for adj in router['adj']:
						if adj['n_id'] == nextR:
							hopsIP.append(adj['peerIP'])
							break
					break
		i+=1
	
	return hopsIP

def getBackupPaths():
	#print "Calculating new Shortest Path"
	
	return backupPaths

#hops, curr = getShortestPath()
#pprint.pprint(routers)
#pprint.pprint(curr['nhop'])
#pprint.pprint(hops)

#print "Backup Shortest Path"
#pprint.pprint(backupPaths)
