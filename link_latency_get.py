'''
Created on Aug 11, 2016

@author: azaringh
'''
import redis
import json

# print last input pps for ge-1/0/5 on Chicago
routers = [ 
           { 'name': 'chicago', 'router_id': '10.210.10.124', 'latitude':'', 'longitude':''},
           { 'name': 'san francisco', 'router_id': '10.210.10.100', 'latitude':'', 'longitude':''},
           { 'name': 'dallas', 'router_id': '10.210.10.106', 'latitude':'', 'longitude':''},
           { 'name': 'miami', 'router_id': '10.210.10.112', 'latitude':'', 'longitude':''},
           { 'name': 'new york', 'router_id': '10.210.10.118', 'latitude':'', 'longitude':''},
           { 'name': 'los angeles', 'router_id': '10.210.10.113', 'latitude':'', 'longitude':''},
           { 'name': 'houston', 'router_id': '10.210.10.114', 'latitude':'', 'longitude':''},
           { 'name': 'tampa', 'router_id': '10.210.10.115', 'latitude':'', 'longitude':''}
           ]


r = redis.StrictRedis(host='10.10.4.252', port=6379, db=0)
#latency_str = r.lrange('san francisco:los angeles:latency', 0, -1)[0]
#print latency_str
#latency_dict = json.loads(latency_str) # decode json; convert json string to python dictionary
#print latency_dict
#print latency_dict['timestamp'], latency_dict['rtt-average(ms)']

def getRTT(r_id1, r_id2):
	r1 = ''
	r2 = ''
	for router in routers:
		if router['router_id'] == r_id1: 
			r1 = router['name']
			break
	
	for router in routers:
		if router['router_id'] == r_id2:
			r2 = router['name']
			break
	code = r1 + ':' +  r2 + ':latency'
	latency={}
	try:
		latency = r.lrange(code, 0, -1)[0]
	except:
		print("Wrong latency code")
		print code
		code = r2 + ":" + r1 +':latency'
		pass		
	latency = r.lrange(code, 0,-1)[0]
	json_latency = json.loads(latency)
	
	return json_latency['rtt-average(ms)']


#print getRTT('10.210.10.114', '10.210.10.115')

