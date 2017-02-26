'''
Created on Feb 20, 2016

@author: azaringh
'''

import redis
import json
import pprint
from link_event_handler import *
from lsp_ospf import *




r = redis.StrictRedis(host='10.10.4.252', port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe('link_event')

recoverEventHandler({})
for item in pubsub.listen():
    print item['channel'], ":", item['data']
    if isinstance(item['data'], basestring):
        d = json.loads(item['data'])
	#eventHandler(d)
        #print "Inside link event client"
	pprint.pprint(d, width=1)
	eventHandler(d)

