import redis
import json
import pprint

# print last input pps for ge-1/0/5 on Chicago
port = 12908
hostname = "redis-12908.c10.us-east-1-4.ec2.cloud.redislabs.com"

r = redis.StrictRedis(host=hostname, port=port, db=0)
router_name = r.get('router')
print router_name # json-formatted string

