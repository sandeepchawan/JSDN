import json
from lsp_rro_get import *
from lsp_check_status import *
import topology
import lsp_ospf as ospf 
import pprint
from lsp_modify_ero import *

test_event = {"status": "failed", "router_id": "10.210.10.118", "timestamp": "Thu:16:57:51", "interface_address": "10.210.17.1", "interface_name": "ge-1/0/2", "router_name": "los angeles"}

shortestIPHops, shortestPath = ospf.getShortestPath()
backupPaths = ospf.getBackupPaths()
backupPath = backupPaths[0]

print "Shortest Path"
pprint.pprint(shortestPath)

print "Backup Path"
pprint.pprint(backupPath)

def eventHandler(event):
        print "Handling new event\n"
	print event
        if(event['status'] == 'failed'):
                print "Link failure detected"
                failoverBackupLSP(event);
        if(event['status'] == 'healed'):
                print "Link Recovered detected"
               	recoverEventHandler(event);

def enableLSP(lspList, path):
	print "Enabling LSPs"
	nhops = ospf.getHopsIP(path['nhop'])
	pathR = path['nhop'][::-1]
	nysfHop = ospf.getHopsIP(pathR)

	#print "Next Hops to enable: "
	#pprint.pprint(nhops)
	#pprint.pprint(nhopsR)
	#print "####"
	for lsp in lspList:
		if 'SF_NY' in lsp['name']:
			modifyLSP(lsp['name'], nhops)
		else:
			modifyLSP(lsp['name'], nysfHop)
	#set current value of shortest path = backup Path
	shortestPath = backupPath

	

def failoverBackupLSP(failEvent):
        print "Response to event handler"
	#saveCurrentLSP(failEvent)
	downIP1 = failEvent['interface_address']
	downIP2 = topology.getPeer(downIP1)
	affect_list = getListAffectLSP(downIP1, downIP2)
	
	#global backupPaths
	global backupPath

	if affect_list:
		#print backupPath
		print "Checking Backup, getting best Backup Path Online:"
		backupIsUp = checkSinglePathOnline(backupPath)
		#If first backup is not up, check whole list
		if backupIsUp == False:
			backupPath = checkBackupOnline(backupPaths)
		
		#pprint.pprint(backupPath)
		#Enable backup list
		enableLSP(affect_list, backupPath)
		
		#pprint.pprint(shortestPath)
		ospf.findNewBackup(shortestPath['nhop'], downIP1, downIP2)
		backupPaths = ospf.getBackupPaths()
		backupPath = backupPaths[0]
	else:
		print "Nothing get Affected, no need to worry"
	
def checkSinglePathOnline(path):
	isUp = False
	isUp = isAllLinkUp(path['nhop'])
	return isUp
	
def checkBackupOnline(paths):
	isUp = False
	for path in paths:
		isUp = isAllLinkUp(path['nhop'])
		if isUp:
			break
	return path
	
	
def recalculateShortestPath():
	print "Recalculate Backup Shortest Path"
	return ospf.getShortestPath()



def recoverEventHandler(healEvent):
	print "Response to Healed Event"
	newIPHops, newSP = recalculateShortestPath()
	print "New calculated path: ", newSP['cost'], "Current Path: ", shortestPath['cost']
	if newSP['cost'] < shortestPath['cost']:
		enableLSP(getCurrentLSPList(), newSP)
		print "Recovered Link have lower cost, enabled new LSP"
	else:
		print "Path already optimized, no need to change"

#eventHandler(test_event)	
