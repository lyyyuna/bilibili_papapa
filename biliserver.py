from bilibilitasks import download
from pymongo import MongoClient
import json
import threading
import Queue
import time
import logging
import logging.config
import sys

logging.config.fileConfig("logger.conf")
logger = logging.getLogger('bili')


client = MongoClient('127.0.0.1', 27017) 
db = client.test
biliusers = db.biliusers
maxmid = db.maxmid
# global queue
q = Queue.Queue(maxsize=4)


class myThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        nextmid = q.get()
        while True:
            result = download.delay(nextmid)
            try:
                response = result.get(90)   
            except Exception, e:
                logger.info("task wait timeout.\n" + str(e))
                print(str(e))
                continue

            # forget result
            result.forget()

            try:
                res_dict = json.loads(response)
            except Exception, e:
                res_dict = {}
                logger.info("Json decode failed.\n" + str(e))
                print(str(e))

            status = res_dict['status'] if 'status' in res_dict.keys() else False
            if status == True:
                if 'data' in res_dict.keys():
                    buser = res_dict['data']
                    if 'face' in buser:
                        del buser['face']
                    if 'toutu' in buser:
                        del buser['toutu']
                    mid = buser['mid']
                    maxmid.replace_one({'max': 'flag'}, {'max': 'flag', 'mid' : str(mid)}, upsert=True)
                    biliusers.replace_one({'mid': mid}, buser, upsert=True)   

            nextmid = q.get() 


for i in range(0, 2):
    thread = myThread()
    thread.start()

while True:
    nextmid = 1
    for doc in db.maxmid.find():
        nextmid = int(doc['mid'])
    if nextmid > 100000:
        logger.info('Finish')
        print ('Finish')
        sys.exit()
    for i in xrange(nextmid, 100000):
        q.put(i)
        time.sleep(1)
        if i%100 == 0:
            print i, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 