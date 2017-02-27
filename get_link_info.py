'''
Created on Aug 12, 2016

@author: azaringh
'''
import requests
requests.packages.urllib3.disable_warnings()
import json
from link_latency_get import *
import pprint


def getNodeNeighbors(nodeId):
	url = "https://10.10.2.29:8443/oauth2/token"

	payload = {'grant_type': 'password', 'username': 'group5', 'password': 'Group5'}
	response = requests.post (url, data=payload, auth=('group5','Group5'), verify=False)
	json_data = json.loads(response.text)
	authHeader= {"Authorization":"{token_type} {access_token}".format(**json_data)}
	r = requests.get('https://10.10.2.29:8443/NorthStar/API/v2/tenant/1/topology/1/links/', headers=authHeader, verify=False)
	links = r.json()	
	
	#pprint.pprint(links)
	neighbors = [] 
	
	#pprint.pprint(links)
	#print "waiting for info"
		
	for link in links:
		if link['operationalStatus'] != "Up":
			continue

		if link['endA']['node']['id'] != nodeId and link['endZ']['node']['id'] != nodeId:
			continue
		elif link['endA']['node']['id'] == nodeId:
			try:
				peer_ip = link['endZ']['ipv4Address']['address']
				local_ip = link['endA']['ipv4Address']['address']
				#bw = 1000000000
				bw = int((link['endZ']['bandwidth'])/100)
				neighbors.append({'localIP':local_ip, 'peerIP': peer_ip, 'n_id': link['endZ']['node']['id'], 'bw': bw})
 
			except Exception as e:
				print "Error when getting Node Neighbors"
				print str(e)
				return

		else: 
			try:
				peer_ip = link['endA']['ipv4Address']['address']
				local_ip = link['endZ']['ipv4Address']['address']
				#bw = 1000000000
				bw = int((link['endA']['bandwidth'])/100)	
				neighbors.append({'localIP':local_ip, 'peerIP': peer_ip, 'n_id': link['endA']['node']['id'], 'bw': bw})
			except Exception as e:
				print "Error when getting node neighbors"
				print str(e)
				return
	
	#if neighbors:
	#	print "FOUND NEIGHBORS of " ,nodeId
	#	pprint.pprint( neighbors)
		
	#print neighbors	
	for neighbor in neighbors:
		rtt = 0
		prior = 5
		#print "nID", nodeId, "neighborId", neighbor['n_id']
		if neighbor['n_id'] is not '':
			rtt = getRTT(nodeId, neighbor['n_id'])
		
		neighbor['reliability'] = 1	
		neighbor['rtt'] = rtt
		#neighbor['r_prior'] = prior
	return neighbors

#pprint.pprint( getNodeNeighbors('10.210.10.112'))
#for link in r.json():
#    if link['name'] == 'L10.210.11.1_10.210.11.2':
#        print 'A node:', link['endA']['node']['name']
#        print 'Z node:', link['endZ']['node']['name']
