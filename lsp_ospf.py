from get_link_info import *
import pprint
from link_latency_get import *
import json
import heapq
from operator import itemgetter
import copy
import random

def shortestPath(start, end,graph):
	#pprint.pprint(graph)
	#print "start:", start, "end: ", end

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

routers = copy.deepcopy(original_routers)

def calculateLinkCost(adj):
	#reference bw, default = 1bps link = 10^9
	ref_bw = 1000000000
	bw = adj['bw']
	rtt = adj['rtt']
	reli = adj['reliability']
	#r_prior = adj['r_prior'] 
	
	#Link cost: ((RTT/20  * 256)    +   reference-bw / reservered-min-bw ) * reliability 
	#priority 1 -> 15, 1 = highest priority = lowest cost
	cost =  ((rtt/20 * 256) + ((ref_bw)/bw)) * reli
	
	return int(cost)


def getRouterAdj(newRouters):
	for router in newRouters:
		#print "getRouterAdj", router['router_id']
		neighbors = getNodeNeighbors(router['router_id'])
		#if len(neighbors) == len(router['adj']):
			#print "**** PROBLEM WITH GETTING NEIGHBORS"
			#pprint.pprint(neighbors)
		for neighbor in neighbors:
			neighbor['cost'] = calculateLinkCost(neighbor)

		router['adj'] = neighbors
		#print "CHECKING NEIGHBORS ADJ"
		#pprint.pprint(router)
		#pprint.pprint(router['adj'])
		#pprint.pprint(neighbors)
	
			

#getRouterAdj()
#pprint.pprint(routers)

topoGraphs = [{}, {}]
backupPaths= [] 

def createTopologyGraph(excRouters = [], ID=0):
	global routers
	global topoGraphs

	routers = copy.deepcopy(original_routers)
	#print "FRESH TOPO?"
	#pprint.pprint(routers)
	if excRouters:
		newRouters = routers
		for excR in excRouters:
			for router in newRouters:
				if router['router_id'] == excR:
					newRouters.remove(router)
					break
		getRouterAdj(newRouters)
	else:
		getRouterAdj(routers)

	#print "Inside creating topo"
	#pprint.pprint(routers)	
	
	#for router in routers:
	#	if not router['adj']:
	#		print "MISSING ROUTER ADJ"
	#		return
	
	topoGraph = {}
	#print "*************** EXC ROUTER *************" , excRouters
	for router in routers:
		adjs = {}
		for adj in router['adj']:
			if adj['n_id'] in excRouters:
				#adjs.update({adj['n_id']: adj['cost']})
				continue
			adjs.update({adj['n_id']:adj['cost']})
			#print "********* FOUND EXC ROUTER ********"
		
		topoGraph.update({router['router_id']: adjs})
	
	if topoGraph:
		topoGraphs[ID] = topoGraph
	try:	
		if not topoGraphs[ID]:
			print "MISSING TOPO GRAPHS"
			return
	except:
		return
	#print "TOPO after running ()"
	#pprint.pprint(topoGraphs[0])
	#pprint.pprint(topoGraphs[1])
	#pprint.pprint(topoGraphs[ID])
	return topoGraphs[ID]	
	
#reateTopologyGraph()
#print "Topology Graph"
#pprint.pprint(topoGraph)
	
#curShortestPath = {}
#curShortestIPHops = [] 
#shortestPath('10.210.10.118','10.210.10.100', topoGraph)
#print "Best Shortest Path"
#print curShortestPath


def calculateBackupSP(curShortestPath, graph):
	#print curShortestPath
	hops = curShortestPath['nhop']
	i = 0
	
	while i < (len(hops) - 1):
		endA = hops[i]
		endZ = hops[i+1]
		newGraph = copy.deepcopy(graph)
		#pprint.pprint(newGraph)
		
		newGraph[endA].pop(endZ, None)
		#print "End A: ", endA, "EndZ" , endZ, 'i', i
		#pprint.pprint(newGraph)
		newSP = {}
		try:
			newSP = shortestPath(hops[0], hops[-1], newGraph)
		except:
			pass
		#pprint.pprint(newSP)
		if i == 0:
			i+=1
			if newSP:
				backupPaths.append(newSP)
			continue
		if i>0:
			if newSP:
				backupPaths.append(newSP)
		i+=1
	
	try:
		sortBackupPaths()
	except:
		pass
	#print "Backuppaths: ", backupPaths
	return backupPaths

def findNewBackup(hops, downIP1, downIP2):
	i=0
	#pprint.pprint(hops)
	while i < (len(hops) - 1):
                endA = hops[i]
                endZ = hops[i+1]
                newGraph = copy.deepcopy(topoGraphs[0])
                newGraph[endA].pop(endZ, None)
		try:
			newGraph[endA].pop(downIP1, None)
			newGraph[endA].pop(downIP2, None)
			newSP = shortestPath(hops[0], hops[-1], newGraph)

			for path in backupPaths:
				if newSP['cost'] == path['cost']:
					backupPaths.remove(path)
			backupPaths.append(newSP)
		except:
                        pass

                i+=1
	
	sortBackupPaths()
	return backupPaths


def sortBackupPaths():
	global backupPaths
	sort_order = ['cost','nhop']
	
	#ynique = {each['cost']: each for each in backupPaths}.values()
	sortedList = []
	for path in backupPaths:
		if path not in sortedList:
			sortedList.append(path)
	#print list(set(backupPaths))
	result = sorted(sortedList, key=itemgetter('cost'))
	#pprint.pprint(backupPaths)
	#backupPathsSorted = [OrderedDict(sorted(item.iteritems(), key=lambda (k, v): sort_order.index(k)))
        #            for item in backupPaths]

	#result = []
	#for item in backupPathsSorted:
	#	i = item.items()
	#	result.append({'cost':i[0][1], 'nhop':i[1][1]})

	#pprint.pprint(result)	
	backupPaths = result



def getShortestPath(noRouter = []):
	print "Refreshing Current Topology.."
	global topoGraphs
	topoGraphs = [{}, {}]
	
	excRouters = []
	if noRouter:
		excRouters.append(noRouter)
	
	createTopologyGraph(excRouters, 0)
	curShortestPath = shortestPath('10.210.10.100','10.210.10.118', topoGraphs[0])

	bestHops = curShortestPath['nhop']

	excR = bestHops[(len(bestHops)-1)/2]

	if excR not in excRouters:
		excRouters.append(excR)
		#print excRouters
	createTopologyGraph(excRouters,1)
	
	shortestPath2 = shortestPath('10.210.10.100','10.210.10.118', topoGraphs[1])

	print "\n*** Shortest Path found:"
	pprint.pprint(curShortestPath)
	pprint.pprint(shortestPath2)

	print "\n Calculating new Backup Paths ..."
	calculateBackupSP(curShortestPath, topoGraphs[0])
 	calculateBackupSP(shortestPath2, topoGraphs[1])
	
	#pprint.pprint(backupPaths)
	#Get a minimum of 5 Backup Paths	
	while len(backupPaths) < 6 :
		#pprint.pprint(backupPaths[-1])
		#print "Loop"
		i = random.randint(0,1)
		
		try:
			for path in backupPaths:
				calculateBackupSP(path, topoGraphs[i])
		except:
			pass

	#Final Swap
	for path in backupPaths:
		if path['cost'] < curShortestPath['cost']:
                        backupPaths.append(curShortestPath)
                        curShortestPath = path
                        backupPaths.remove(path)
	sortBackupPaths()	

	for path2 in backupPaths:
		if path2['cost'] < shortestPath2['cost'] and path2['cost'] > curShortestPath['cost']:
			backupPaths.append(shortestPath2)	
			shortestPath2 = path2
			backupPaths.remove(path2)
	
	if curShortestPath['cost'] > shortestPath2['cost']:
		temp = copy.deepcopy(curShortestPath)
		curShortestPath = shortestPath2
		shortestPath2 = temp
	for pathH in backupPaths:
		if pathH['cost'] <= shortestPath2['cost']:
			backupPaths.remove(pathH)

	sortBackupPaths()
	ipHops1 = getHopsIP(curShortestPath['nhop'])
        ipHops2 = getHopsIP(shortestPath2['nhop'])
	
	#print "Finalized Backup Paths:" 
	#pprint.pprint(backupPaths)

	return ipHops1, curShortestPath, ipHops2, shortestPath2

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
