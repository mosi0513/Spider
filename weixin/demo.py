from requests import Session
from urllib.parse import urlencode
from Weixin_request import Weixin_Request
from weixin_queue import RedisQueue
from pyquery import PyQuery as pq
import requests
from requests import ConnectionError, ReadTimeout
from config import *

# create object
class Spider():



    base_url = 'http://weixin.sogou.com/weixin'
    headers = {
        'Cookie': 'ABTEST=0|1528628814|v1; SNUID=02FDB54DE7E389A1469EE9AAE7F54A49; IPLOC=CN4201; SUID=E41A53AB4942910A000000005B1D064E; SUID=E41A53AB4F18910A000000005B1D064F; SUV=005351ECAB531AE45B1D0651ED127317; weixinIndexVisited=1; sct=1; JSESSIONID=aaa-FKMJcBPJ27jXbTknw; ppinf=5|1528633409|1529843009|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxODolRTclQTMlQTglRTYlOTYlQUZ8Y3J0OjEwOjE1Mjg2MzM0MDl8cmVmbmljazoxODolRTclQTMlQTglRTYlOTYlQUZ8dXNlcmlkOjQ0Om85dDJsdVAtUGp3emJ1dXZEeDZ6M3V2bHpDLWdAd2VpeGluLnNvaHUuY29tfA; pprdig=x75NJVfeUeiVx_6GfNqTogw7mx9zZIFhBNJ55CVelgKHdJOYvyVpv0tG-t6idOyRG2_xuEtgH9gr57ndSEJyYZ_6DxZSZFGmS6egieMYSxFylTbsoC6KWj8dL3BsIupQzMJBvE1u-8zS31GzGf0wbCtKIP-3Lcb9Uq6reSmc3Yk; sgid=11-35352387-AVsdGEGfJgTI0bgDyAJRfgs; ppmdig=15286334110000009e3d8abb4bc85606a586fada63ec8ebf',
        'Host': 'weixin.sogou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }
    keyword = 'Python'

    #  keep cookied
    session = Session()
    queue = RedisQueue()
# svae to mongodb
    def save_to_mongo(self,infos):
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client.doubanmusic
        collection = db.people
        collection.insert_many([infos])


def parse_html(self,page):
    data = {

        'query': self.keyword,
        'type': '2',
        'page': page
    }
    url = self.base_url + '?' + urlencode(data)

def