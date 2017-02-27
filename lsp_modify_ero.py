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



def modifyLSP(name, hops):
        #print name, hops
	ero = []
	for lsp in lsp_list:
		if lsp['name'] == name:
			break
	#print hops
        for ip in hops:
		#print "looking at IP: ", ip
		if ip != hops[0] and ip != hops[-1]:
                	ero.append({'topoObjectType':'ipv4', 'address':str(ip)})

        new_lsp = {}
        for key in ('from', 'to', 'name', 'lspIndex', 'pathType'):
                new_lsp[key] = lsp[key]
	
	#print ero

        new_lsp['plannedProperties'] = {
                'ero': ero
        }
	
	#pprint.pprint(new_lsp)
	
        response = requests.put('https://10.10.2.29:8443/NorthStar/API/v2/tenant/1/topology/1/te-lsps/' + str(new_lsp['lspIndex']), json = new_lsp, headers=authHeader, verify=False)
        
	#if "400" in response:
	#	print "***** BAD REQUEST *******"
	#	pprint.pprint(new_lsp)
	pprint.pprint(response)
	#pprint.pprint(new_lsp) 
	#pprint.pprint(response)
	#print "Sent new LSP"
	

