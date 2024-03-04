import json

import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, Form
from pydantic import HttpUrl
from pydantic import BaseModel

from ..utils import utility

router = APIRouter()

class PHVideo(BaseModel):
    text: str
    url: HttpUrl


@router.post('/real-url', response_model=PHVideo)
async def real_url(url: HttpUrl = Form()):
    ses = requests.session()
    res = ses.get(url)
    res.raise_for_status()
    
    soup = BeautifulSoup(res.text, 'lxml')
    js = soup.select_one('#player.original.mainPlayerDiv script').string
    
    # extract json from js
    js = js.split('\n')[1]
    js = js[js.find('{'):-1]
    js = json.loads(js)
    
    for m in js['mediaDefinitions']:
        if m.get('remote', False):
            remote_url = m['videoUrl']

    res = ses.get(remote_url)
    res.raise_for_status()
    max = None
    for m in res.json():
        max = m if not max else max if int(max['quality']) > int(m['quality']) else m
    return PHVideo(utility.handle_title(soup.title.string[:soup.title.string.find(' - Pornhub.com')]), max['videoUrl'])
