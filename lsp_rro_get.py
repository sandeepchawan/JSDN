'''
Created on Aug 12, 2016

@author: azaringh
'''
import requests
requests.packages.urllib3.disable_warnings()
import json
from lsp_check_status import *

url = "https://10.10.2.29:8443/oauth2/token"

payload = {'grant_type': 'password', 'username': 'group5', 'password': 'Group5'}
response = requests.post (url, data=payload, auth=('group5','Group5'), verify=False)
json_data = json.loads(response.text)
authHeader= {"Authorization":"{token_type} {access_token}".format(**json_data)}

r = requests.get('https://10.10.2.29:8443/NorthStar/API/v2/tenant/1/topology/1/te-lsps/', headers=authHeader, verify=False)

p = json.dumps(r.json())
lsp_list = json.loads(p)
# Find target LSP to use lspIndex

#for lsp in lsp_list:
#    if lsp['name'] == 'GROUP_NINE_NY_SF_LSP4':
#        break   
#print json.dumps(lsp, indent=4, separators=(',', ': '))
#print lsp['liveProperties']['rro']
#count = 1
#for nhop in lsp['liveProperties']['rro']:
#    print 'hop' + str(count) + ':', nhop['address']
#    count = count + 1


backupLSP = {}

def getCurrentLSP():
	currentLSP = {}
	for lsp in lsp_list:
		if "FIVE" in lsp['name']:
			nhopList = []
			for nhop in lsp['liveProperties']['rro']:
				nhopList.append(nhop['address'])
			currentLSP[lsp['name']] =  nhopList
	print "Current LSP"
	print currentLSP	
	return currentLSP

currentLSP = getCurrentLSP()

#print "Here current LSP: \n"
#print currentLSP


def calculateBackupLSP():
	#backupLSP = currentLSP
	print "**** THIS IS BACKUP LINK ****"
	print backupLSP

def checkAltLSPStatus(name):
	allUp = True

        nhop_list = []
	#print currentLSP.get(name)
	#print backupLSP.get(name)
        for nhop in backupLSP.get(name):
        	#print "NEXT HOP" , nhop
		nhop_list.append(nhop)

        if not isAllLinkUp(nhop_list):
                allUp = False

        return allUp

def upOldBestLSP(name):
	print "Getting old best LSP up"
	
	nhop_list = [] 
	allUp = True
	
	for nhop in bestOldLSP.get(name):
		nhop_list.append(nhop)

	if not isAllLinkUp(nhop_list):
		allUp = False
	print "Checked. All Old Best LSP Link is Up ? - " , allUp

	if allUp:
		for lsp in lsp_list:
                	if lsp['name'] == name:
                        	break
        	ero = []

        	for ip in bestOldLSP[name]:
                	ero.append({'topoObjectType': 'ipv4', 'address':ip})

        	new_lsp = {}
        	for key in ('from', 'to', 'name', 'lspIndex', 'pathType'):
                	new_lsp[key] = lsp[key]

        	new_lsp['plannedProperties'] = {
                	'ero': ero
        	}
        	response = requests.put('https://10.10.2.29:8443/NorthStar/API/v2/tenant/1/topology/1/te-lsps/' + str(new_lsp['lspIndex']), json = new_lsp, headers=authHeader, verify=False)		
		
			

def upBackupLSP(name):
	
	print "Is this" , name, " Backup Link Up?", checkAltLSPStatus(name)
	for lsp in lsp_list:
		if lsp['name'] == name:
			break
	ero = []
	
	for ip in backupLSP[name]:
		ero.append({'topoObjectType': 'ipv4', 'address':ip})

	new_lsp = {}
	for key in ('from', 'to', 'name', 'lspIndex', 'pathType'):
		new_lsp[key] = lsp[key]
	
	new_lsp['plannedProperties'] = {
		'ero': ero
	}
	response = requests.put('https://10.10.2.29:8443/NorthStar/API/v2/tenant/1/topology/1/te-lsps/' + str(new_lsp['lspIndex']), json = new_lsp, headers=authHeader, verify=False)
	
	#print response.text




def getListAffectLSP(downIP1, downIP2):
	affectLSP  = []
	print currentLSP
	
	for lsp in currentLSP.iterkeys():
		#for hopList in currentLSP.itervalues():
		print "LSP here", lsp
		hopList = currentLSP[lsp]
		if(downIP1 in hopList) or (downIP2 in hopList):
			affectLSP.append({'name':lsp, 'nhop': hopList})	
			#if (downIP1 in hopList) or (downIP2 in hopList):
			#	affectLSP.append({'name':lsp, 'nhop': hopList})
			#	
			#	print "Find an affect LSP", lsp, hopList

	print "Affect LSP #: ", affectLSP
	return affectLSP

def getNextHopList(lspName):
	return currentLSP[lspName]

#getListAffectLSP('10.210.20.1', '10.210.20.2')

