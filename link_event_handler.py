import json
from lsp_rro_get import *
from lsp_check_status import *
import topology
import lsp_ospf as ospf 
import pprint

test_event = {"status": "failed", "router_id": "10.210.10.118", "timestamp": "Thu:16:57:51", "interface_address": "10.210.17.1", "interface_name": "ge-1/0/2", "router_name": "los angeles"}

shortestPath = ospf.getShortestPath()
backupPaths = ospf.getBackupPaths()
print "Shortest Path"
pprint.pprint(shortestPath)

print "Backup Path"
pprint.pprint(backupPaths)

def eventHandler(event):
        print "Handling new event\n"
	print event
        if(event['status'] == 'failed'):
                print "Link failure detected"
                failoverBackupLSP(event);
        if(event['status'] == 'healed'):
                print "Link Recovered detected"
                bringBackOldLSP(event);

def enableBackupLSP(name):
	print "Enabling backup LSP"
	upBackupLSP(name)

def failoverBackupLSP(failEvent):
        print "Response to event handler"
	#saveCurrentLSP(failEvent)
	downIP1 = failEvent['interface_address']
	downIP2 = topology.getPeer(downIP1)
	affect_list = getListAffectLSP(downIP1, downIP2)
	
	if affect_list:
		print "Checking Backup"
		checkBackupOnline(backupPaths)
	#checkBackupAvailability(backupPaths)
	#bringUpBackup()
	#recalculateShortestPath()
	
def checkBackupOnline(paths):
	isUp = False
	for path in paths:
		isUp = isAllLinkUp(path['nhop'])
		if isUp:
			break
	return path
		
def recalculateShortestPath():
	print "Recalculate Shortest Path"
	

def saveCurrentLSP(event):
        print "Saving current LSP"

	downIP1 = event['interface_address']
	downIP2 = topology.getPeer(downIP1)
	print downIP1, downIP2
	
	affect_list = getListAffectLSP(downIP1,downIP2)
 	#print "Is All Backup Link Up?", checkAltLSPStatus(affect_list)
	
	for affectlsp in affect_list:
		enableBackupLSP(affectlsp['name'])
		print "Affected LSP: ", affectlsp
	#print "Is All Link Up?", checkAltLSPStatus(affect_list)
	
	
def bringBackOldLSP(healEvent):
	print "Heal Event response"

eventHandler(test_event)	
