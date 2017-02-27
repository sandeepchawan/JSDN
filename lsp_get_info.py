import requests
requests.packages.urllib3.disable_warnings()
import json
from lsp_check_status import *
import pprint
url = "https://10.10.2.29:8443/oauth2/token"

payload = {'grant_type': 'password', 'username': 'group5', 'password': 'Group5'}
response = requests.post (url, data=payload, auth=('group5','Group5'), verify=False)
json_data = json.loads(response.text)
authHeader= {"Authorization":"{token_type} {access_token}".format(**json_data)}

r = requests.get('https://10.10.2.29:8443/NorthStar/API/v2/tenant/1/topology/1/te-lsps/', headers=authHeader, verify=False)

p = json.dumps(r.json())
lsp_list = json.loads(p)

routers = [ 
           { 'name': 'chicago', 'router_id': '10.210.10.124', 'interfaces': [
                                                                            { 'name': 'ge-1/0/1', 'address': '10.210.16.2' }, 
                                                                            { 'name': 'ge-1/0/2', 'address': '10.210.13.2' },
                                                                            { 'name': 'ge-1/0/3', 'address': '10.210.14.2' }, 
                                                                            { 'name': 'ge-1/0/4', 'address': '10.210.17.2' }
                                                                            ] 
            },
           { 'name': 'san francisco', 'router_id': '10.210.10.100', 'interfaces': [
                                                                            { 'name': 'ge-1/0/0', 'address': '10.210.18.1' },
                                                                            { 'name': 'ge-1/0/1', 'address': '10.210.15.1' },
                                                                            { 'name': 'ge-1/0/3', 'address': '10.210.16.1' }
                                                                            ]
            },
           { 'name': 'dallas', 'router_id': '10.210.10.106', 'interfaces': [
                                                                             { 'name': 'ge-1/0/0', 'address': '10.210.15.2' }, 
                                                                             { 'name': 'ge-1/0/1', 'address': '10.210.19.1' }, 
                                                                             { 'name': 'ge-1/0/2', 'address': '10.210.21.1' }, 
                                                                             { 'name': 'ge-1/0/3', 'address': '10.210.11.1' }, 
                                                                             { 'name': 'ge-1/0/4', 'address': '10.210.13.1' }
                                                                             ] 
            },
           { 'name': 'miami', 'router_id': '10.210.10.112', 'interfaces': [
                                                                            { 'name': 'ge-1/0/0', 'address': '10.210.22.1' }, 
                                                                            { 'name': 'ge-1/0/1', 'address': '10.210.24.1' }, 
                                                                            { 'name': 'ge-1/0/2', 'address': '10.210.12.1' }, 
                                                                            { 'name': 'ge-1/0/3', 'address': '10.210.11.2' }, 
                                                                            { 'name': 'ge-1/0/4', 'address': '10.210.14.1' }
                                                                            ] 
            },
           { 'name': 'new york', 'router_id': '10.210.10.118', 'interfaces': [
                                                                               { 'name': 'ge-1/0/3', 'address': '10.210.12.2' }, 
                                                                               { 'name': 'ge-1/0/5', 'address': '10.210.17.1' }, 
                                                                               { 'name': 'ge-1/0/7', 'address': '10.210.26.1' }
                                                                               ] 
            },
           { 'name': 'los angeles', 'router_id': '10.210.10.113', 'interfaces': [
                                                                                  { 'name': 'ge-1/0/0', 'address': '10.210.18.2' },
                                                                                  { 'name': 'ge-1/0/1', 'address': '10.210.19.2' },
                                                                                  { 'name': 'ge-1/0/2', 'address': '10.210.20.1' }
                                                                                  ]
            },
           { 'name': 'houston', 'router_id': '10.210.10.114', 'interfaces': [
                                                                              { 'name': 'ge-1/0/0', 'address': '10.210.20.2' },
                                                                              { 'name': 'ge-1/0/1', 'address': '10.210.21.2' },
                                                                              { 'name': 'ge-1/0/2', 'address': '10.210.22.2' },
                                                                              { 'name': 'ge-1/0/3', 'address': '10.210.25.1' }
                                                                              ] 
            },
           { 'name': 'tampa', 'router_id': '10.210.10.115', 'interfaces': [
                                                                            { 'name': 'ge-1/0/0', 'address': '10.210.25.2' }, 
                                                                            { 'name': 'ge-1/0/1', 'address': '10.210.24.2' }, 
                                                                            { 'name': 'ge-1/0/2', 'address': '10.210.26.2' }
                                                                            ]
            }
           ]


currentLSP = {}

for lsp in lsp_list:
	if "FIVE" in lsp['name']:
		nhopList = []
		for nhop in lsp['liveProperties']['rro']:
			for router in routers:
				for interface in router['interfaces']:
					if interface['address'] == nhop['address']:
						nhopList.append({'router_id': router['router_id'], 'name': router['name'], 'hopIP': nhop['address']})
						break
		currentLSP[lsp['name']] =  nhopList

pprint.pprint(currentLSP)
