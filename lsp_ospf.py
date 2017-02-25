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


routers = [
           { 'name': 'Chicago', 'router_id': '10.210.10.124', 'adj': []},
           { 'name': 'SF', 'router_id': '10.210.10.100','adj': []},
           { 'name': 'Dallas', 'router_id': '10.210.10.106','adj': []},
           { 'name': 'Miami', 'router_id': '10.210.10.112','adj': []},
           { 'name': 'NY', 'router_id': '10.210.10.118','adj': []},
           { 'name': 'LA', 'router_id': '10.210.10.113','adj': []},
           { 'name': 'Houston', 'router_id': '10.210.10.114','adj': []},
           { 'name': 'Tampa', 'router_id': '10.210.10.115','adj': []}
           ]


def calculateLinkCost(adj):
	#reference bw, default = 1bps link = 10^9
	ref_bw = 1000000000
	bw = adj['bw']
	rtt = adj['rtt']
	r_prior = adj['r_prior'] 
	
	#Link cost: ((RTT/20  * 256)    +   reference-bw / reservered-min-bw ) * router-priority 
	#priority 1 -> 15, 1 = highest priority = lowest cost
	cost =  ((rtt/20 * 256) + ((ref_bw)/bw)) * r_prior
	
	return int(cost)


def getRouterAdj():
	for router in routers:
		#print "getRouterAdj", router['router_id']
		neighbors = getNodeNeighbors(router['router_id'])
		for neighbor in neighbors:
			neighbor['cost'] = calculateLinkCost(neighbor)

		router['adj'] = neighbors
			

getRouterAdj()
#pprint.pprint(routers)

topoGraph = {}
backupPaths= [] 

def createTopologyGraph():
	for router in routers:
		cost = {}
		for adj in router['adj']:
			cost.update({adj['n_id']: adj['cost']})
			
		topoGraph.update({router['router_id']: cost})
			
createTopologyGraph()
#print "Topology Graph"
#pprint.pprint(topoGraph)
	
curShortestPath = shortestPath('10.210.10.118','10.210.10.100', topoGraph)
#print "Best Shortest Path"
#print curShortestPath
#print calculateOSPF(topoGraph, '10.210.10.118', '10.210.10.100');

def calculateBackupSP():
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

calculateBackupSP()

def getShortestPath():
	return curShortestPath

def getBackupPaths():
	return backupPaths



#print "Backup Shortest Path"
#pprint.pprint(backupPaths)
