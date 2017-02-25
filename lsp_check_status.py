import requests
requests.packages.urllib3.disable_warnings()
import json


url = "https://10.10.2.29:8443/oauth2/token"

payload = {'grant_type': 'password', 'username': 'group5', 'password': 'Group5'}
response = requests.post (url, data=payload, auth=('group5','Group5'), verify=False)
json_data = json.loads(response.text)
authHeader= {"Authorization":"{token_type} {access_token}".format(**json_data)}

r = requests.get('https://10.10.2.29:8443/NorthStar/API/v2/tenant/1/topology/1/links/', headers=authHeader, verify=False)

p = json.dumps(r.json())
links = json.loads(p)

def refresh():
	r = requests.get('https://10.10.2.29:8443/NorthStar/API/v2/tenant/1/topology/1/links/', headers=authHeader, verify=False)

	p = json.dumps(r.json())
	links = json.loads(p)	

def getLinkStatus(ip1,ip2):
	for link in links:
		if(link['endA']['ipv4Address']['address']== ip1 and link['endZ']['ipv4Address']['address'] == ip2) or (link['endA']['ipv4Address']['address'] == ip2 and link['endZ']['ipv4Address']['address'] == ip1):
			return link['operationalStatus']

def isAllLinkUp(link_list):
	refresh()
	i = 0
	list_size = len(link_list)
	while(i < list_size - 2):	
		isUp = getLinkStatus(link_list[i], link_list[i+1])
		i+= 1
		if isUp == False:
			return False
		
	return True
	
#print getLinkStatus('10.210.22.1', '10.210.22.2')


