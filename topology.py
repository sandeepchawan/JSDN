'''
Created on Feb 21, 2016

@author: azaringh
'''

'''
Retrieve topology of the network
'''

import requests
requests.packages.urllib3.disable_warnings()
import json

url = "https://10.10.2.29:8443/oauth2/token"

payload = {'grant_type': 'password', 'username': 'group5', 'password': 'Group5'}
response = requests.post (url, data=payload, auth=('group5','Group5'), verify=False)
json_data = json.loads(response.text)
authHeader= {"Authorization":"{token_type} {access_token}".format(**json_data)}

r = requests.get('https://10.10.2.29:8443/NorthStar/API/v2/tenant/1/topology/1', headers=authHeader, verify=False)
r_links = requests.get('https://10.10.2.29:8443/NorthStar/API/v2/tenant/1/topology/1/links/', headers=authHeader, verify=False)

topo =  json.dumps(r.json(), indent=4, separators=(',', ': '))

links = json.loads(json.dumps(r_links.json()));
#print topo
#print links

def getPeer(ip):
	endA = ip
	endZ = ''
	for link in links:	
		if link['endA']['ipv4Address']['address'] == endA:
			endZ = link['endZ']['ipv4Address']['address']
			break;
	#print 'END Z = ', endZ
	return endZ;



			
		
