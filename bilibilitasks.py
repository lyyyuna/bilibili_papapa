from celery import Celery
import requests
import time


app = Celery('tasks',
            broker='redis://:Trend%23100@139.129.44.194:80/0',
            backend='redis://:Trend%23100@139.129.44.194:80/0')
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
                data=payload
        ).text
    except Exception:
        print ('Network error.')
        response = 'ERROR'
    time.sleep(1.1)
    return response