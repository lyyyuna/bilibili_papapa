from celery import Celery
import requests
import time
import config

app = Celery('tasks',
            broker=config.server,
            backend=config.server)
app.conf.CELERY_TASK_RESULT_EXPIRES = 300
url = 'http://space.bilibili.com/ajax/member/GetInfo'


@app.task
def download(i):
    payload = {
        '_' : str(int(time.time()*1000)), 
        'mid' : str(i)
    }
    
    try:
        response = requests.post(
                url,
                headers={'Referer': 'http://space.bilibili.com/'+str(i)+'/'},
                data=payload,
                timeout=20
        ).text
    except Exception, e:
        print ('Network error.')
        response = str(e)
    time.sleep(config.task_sleep)
    return response