from bilibilitasks import download
from pymongo import MongoClient
import json

import logging
import logging.config

logging.config.fileConfig("logger.conf")
logger = logging.getLogger('bili')


client = MongoClient('127.0.0.1', 27017) 
db = client.test
biliusers = db.biliusers
maxmid = db.maxmid






result = download.delay(1)
response = result.get(90)   
try:
    res_dict = json.loads(response)
except Exception, e:
    res_dict = {}
    logger.info("Json decode failed." + str(e))
    print(str(e))

status = res_dict['status'] if 'status' in res_dict.keys() else False
if status == True:
    if 'data' in res_dict.keys():
        buser = res_dict['data']
        if 'face' in buser:
            del buser['face']
        if 'toutu' in buser:
            del buser['toutu']
        
        maxmid.replace_one({'max': 'flag'}, {'max': 'flag', 'mid' : '0'}, upsert=True)
        biliusers.insert_one(res_dict['data'])    