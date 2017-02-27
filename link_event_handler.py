import json
from lsp_rro_get import *
from lsp_check_status import *
import topology
import lsp_ospf as ospf 
import pprint
from lsp_modify_ero import *

#test_event = {"status": "failed", "router_id": "10.210.10.118", "timestamp": "Thu:16:57:51", "interface_address": "10.210.17.1", "interface_name": "ge-1/0/2", "router_name": "los angeles"}

shortestIPHops, shortestPath, ipHops2, shortestPath2 = ospf.getShortestPath()

backupPaths = ospf.getBackupPaths()

#Backup Path starts from #2 backup 
if backupPaths[0]['cost'] < backupPaths[1]['cost']:
	backupPath1 = backupPaths.pop(0)
	backupPath2 = backupPaths.pop(0)
else:
	backupPath2 = backupPaths.pop(0)
        backupPath1 = backupPaths.pop(0)	

print "*** Shortest Path ***"
print " - High Priority - "
pprint.pprint(shortestPath)
print " - Low Priority - "
pprint.pprint(shortestPath2)

print "\n*** Backup Paths for High and Low Priority LSP ***"
pprint.pprint(backupPath1)
pprint.pprint(backupPath2)

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


def eventHandler(event):
        print "\n****** New Event received, handling new event ******"
	print event
        if(event['status'] == 'failed'):
                print "Link failure detected"
                failoverBackupLSP(event);
        if(event['status'] == 'healed'):
                print "Link Recovered detected"
               	recoverEventHandler(event);

def enableLSP(lspList, path):
	print "Enabling LSPs"
	#for lsp in lspList:
	#	print "LSP List: ", lsp['name'], "Path: ", path

	nhops = ospf.getHopsIP(path['nhop'])
	pathR = path['nhop'][::-1]
	nysfHop = ospf.getHopsIP(pathR)

	#print "Next Hops to enable: "
	#pprint.pprint(nhops)
	#pprint.pprint(nhopsR)
	#print "####"
	for lsp in lspList:
		if 'SF_NY' in lsp['name']:
			print "Modifying", lsp['name'], nhops
			modifyLSP(lsp['name'], nhops)
		elif 'NY_SF' in lsp['name']:
			print "Modifying", lsp['name'], nysfHop
			modifyLSP(lsp['name'], nysfHop)
	#set current value of shortest path = backup Path
	#shortestPath = path
	#print "Current Shortest Routers Path: ", path['nhop']
	

def failoverBackupLSP(failEvent):
	downIP1 = failEvent['interface_address']
	downIP2 = topology.getPeer(downIP1)
	affect_list = getListAffectLSP(downIP1, downIP2)
	
	#global backupPaths
	global backupPath1
	global backupPath2

	if affect_list:
		print "Link failure affects LSP(s), bring up backup ..."
		highPriorLSP = []
		for lsp in affect_list:
			if "1" in lsp['name'] or ['2'] in lsp['name']:
				highPriorLSP.append(lsp)
				affect_list.remove(lsp)
		
		#Deal with high priority path first		
		if highPriorLSP:
			backupIsUp = checkSinglePathOnline(backupPath1)
			#If main backup not detected, going down the backup list
			if backupIsUp == False:
				backupPath1 = checkBackupOnline(backupPaths)

			enableLSP(highPriorLSP, backupPath1)
			shortestPath = backupPath1
			print "Affected High Prioriry LSP Backup is Up and Running"
		
		#Now deal with Low Priority:
		backupIsUp = checkSinglePathOnline(backupPath2)
		if backupIsUp == False:
			backupPath2 = checkBackupOnline(backupPaths)

		#Enable backup list
		enableLSP(affect_list, backupPath2)
		print "Affected Low Priority LSP Backup is Up and Running"
		shortestPath2 = backupPath2
		#pprint.pprint(shortestPath)
		ospf.findNewBackup(shortestPath['nhop'], downIP1, downIP2)
		backupPaths = ospf.getBackupPaths()
		
		if backupPaths[0]['cost'] < backupPaths[1]['cost']:
        		backupPath1 = backupPaths.pop(0)
       			backupPath2 = backupPaths.pop(0)
		else:
        		backupPath2 = backupPaths.pop(0)
	        	backupPath1 = backupPaths.pop(0)


	else:
		print "~~ Link Failure did not affect any LSP, no need to worry ~~ "
	
blockR = ''
	
def recalculateShortestPath():
	global blockR

	if blockR != '':
		return ospf.getShortestPath(blockR)

	print "Recalculate Backup Shortest Path"
	return ospf.getShortestPath()



def recoverEventHandler(healEvent):
	print "Response to Healed Event"
	try:
		newIPHops, newSP, newIPHops2, newSP2 = recalculateShortestPath()
	except:
		print "Something Happen, Try again"
		return
	
	global shortestPath
	print "New calculated path: ", newSP['cost'], "Current Path: ", shortestPath['cost']

	if newSP['cost'] <= shortestPath['cost']:
		shortestPath = newSP 
		shortestPath2 = newSP2

		backupPaths = ospf.getBackupPaths()
		if backupPaths[0]['cost'] < backupPaths[1]['cost']:
                        backupPath1 = backupPaths.pop(0)
                        backupPath2 = backupPaths.pop(0)
                else:
                	backupPath2 = backupPaths.pop(0)
                        backupPath1 = backupPaths.pop(0)
		
		lspList = getCurrentLSPList()
		pprint.pprint(lspList)
		highPrior = []
		for lsp in lspList:
			if "1" in lsp['name'] or "2" in lsp['name']:
				#print "High Prior LSP: ", lsp
				highPrior.append(lsp)
				lspList.remove(lsp)

		enableLSP(highPrior, shortestPath)
		enableLSP(lspList, shortestPath2)
		
		print "Recovered Link have lower cost, enabled new LSP"
	else:
		print "Path already optimized, no need to change"

def refreshPaths():
	recoverEventHandler({})


def setBlockRouter(r_id):
	global blockR
	blockR = r_id
	
	newIPHops, newSP, newIPHops2, newSP2 = recalculateShortestPath()
	#CHANGE EVERYTHING
	if newIPHops and newSP and newIPHops2 and newSP2:	
		shortestPath = newSP
        	shortestPath2 = newSP2

                backupPaths = ospf.getBackupPaths()
                if backupPaths[0]['cost'] < backupPaths[1]['cost']:
                        backupPath1 = backupPaths.pop(0)
                        backupPath2 = backupPaths.pop(0)
                else:
                        backupPath2 = backupPaths.pop(0)
                        backupPath1 = backupPaths.pop(0)

                lspList = getCurrentLSPList()
		highPrior = []
                for lsp in lspList:
                        if "1" in lsp['name'] or "2" in lsp['name']:
                                #print "High Prior LSP: ", lsp
                                highPrior.append(lsp)
                                lspList.remove(lsp)
		pprint.pprint(shortestPath)
                enableLSP(highPrior, shortestPath)
                enableLSP(lspList, shortestPath2)
	else:
		print "Error in setting block Router"
		return
	print "Recalculated shortest Path and backup with blocked Routers"
	print "All LSP Enabled with new Hops"

	#recoverEventHandler({})

refreshPaths()
#refreshPaths()

#setBlockRouter('10.210.10.124')
#eventHandler(test_event)	
