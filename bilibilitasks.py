from celery import Celery
import requests
import time
import config

app = Celery('tasks',
            broker=config.server,
            backend=config.server)
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
    except Exception:
        print ('Network error.')
        response = 'ERROR'
    time.sleep(1.5)
    return response