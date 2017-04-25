from bilibilitasks import download, config
from pymongo import MongoClient
import json
import threading
import Queue
import time
import logging
import logging.config
import sys
import copy

logging.config.fileConfig("logger.conf")
logger = logging.getLogger('bili')


client = MongoClient('127.0.0.1', 27017) 
db = client.test
biliusers = db.biliusers
maxmid = db.maxmid
# global queue
q = Queue.Queue(maxsize=4)
# mongoq
mongoq = []
lock = threading.Lock()


class mongoThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            if lock.acquire():
                logger.info('Msg in queue are: ' + str(len(mongoq)))
                tmpmongoq = copy.deepcopy(mongoq)
                del mongoq[:]
                lock.release()
                mid = -1
                for buser in tmpmongoq:
                    bmid = buser['mid']
                    if int(bmid) > mid:
                        mid = int(bmid)
                if mid is not -1:
                    maxmid.replace_one({'max': 'flag'}, {'max': 'flag', 'mid' : str(mid)}, upsert=True)
                    biliusers.insert_many(tmpmongoq)
            time.sleep(3)


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
                logger.info("Json decode failed.\n" + str(e) + ' \n' + str(nextmid) + '\n' + response)
                print(str(e))

            status = res_dict['status'] if 'status' in res_dict.keys() else False
            if status == True:
                if 'data' in res_dict.keys():
                    buser = res_dict['data']
                    if 'face' in buser:
                        del buser['face']
                    if 'toutu' in buser:
                        del buser['toutu']
                    if lock.acquire():
                        mongoq.append(buser)
                        lock.release()

            nextmid = q.get() 


for i in range(0, config.thread_num):
    thread = myThread()
    thread.start()

recorder = mongoThread()
recorder.start()

while True:
    nextmid = 1
    for doc in db.maxmid.find():
        nextmid = int(doc['mid'])
    if nextmid > 40000000:
        logger.info('Finish')
        print ('Finish')
        sys.exit()
    for i in xrange(nextmid, 40000000):
        q.put(i)
        time.sleep(config.queue_sleep)
        print (i)
        if i%100 == 0:
            print i, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 