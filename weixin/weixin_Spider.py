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
    page = 1

    #  keep cookied
    session = Session()
    queue = RedisQueue()
# svae to mongodb
    def save_to_mongo(self,infos):
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client.doubanmusic
        collection = db.people
        collection.insert_many([infos])

# get url
    def parse_html(self):
        data = {
            'query': self.keyword,
            'type': '2',
            'page': self.page
        }
        url = self.base_url + '?' + urlencode(data)
        return url



#  start item
    def start(self):
        #  update cookies
        self.session.headers.update(self.headers)
        url = self.parse_html()
        weixin_request = Weixin_Request(url=url, callback=self.parse_index, need_proxy=True)
        self.queue.add(weixin_request)

#  schedule request
    def schedule(self):
        while not self.queue.empty():
            weixin_request = self.queue.pop()
            callback = weixin_request.callback
            response = self.request(weixin_request)
            if response and response.status_code in VALID_STATUSES:
                results = list(callback(response))# 解析之后形成一个列表
                if results:#如果条件为真
                    for result in results:
                        print('New Resust', type(result))
                    if isinstance(result, Weixin_Request):
                        self.queue.add(result)
                    if isinstance(result, dict):
                        self.save_to_mongo(result)
                else:
                    self.error(weixin_request)
            else:
                self.error(weixin_request)


#  error handle
    def error(self, weixin_request):
        weixin_request.fail_time = weixin_request.fail_time + 1
        #  请求失败的次数 + 请求的url
        print('Request Faild', weixin_request.fail_time, 'Times', weixin_request.url)
        if weixin_request.fail_time < MAX_FAILED_TIME:
            self.queue.add(weixin_request)


#  send request
    def request(self,weixin_request):
        try:
            if weixin_request.need_proxy:
                proxy = self.get_proxy()
                if proxy:
                    proxies = {
                        'http': 'http://' + proxy,
                        'https':'https://'+ proxy
                    }
                    #  谁调用返回给谁，1.weixin_request请求本身的的一些参数， 2.weixin_request对象本身的超出时间 3.不设置自动跳转 4.传入代理ip
                    return self.session.send(weixin_request.prepare(), timeout=weixin_request.timeout, allow_redirects=False, proxies=proxies)
                #  如果不需要代理，则返回need_proxy 为假的请求对象
                return  self.session.send(weixin_request.prepare(), timeout=weixin_request.timeout, allow_redirects=False)
        except(ConnectionError, ReadTimeout) as e:
            print(e.args)#  出现一场已元组的形式打印出来
            return False


#  from proxy pool get proxy
    def get_proxy(self):

        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                print('Get proxy', response.text)
                return response.text#  谁调用返回给谁
            return None
        except requests.ConnectionError:
            return None


#  parse index
    def parse_index(self, response):
        # 1. conversion
        doc = pq(response.text)
        #  items() 类似于一种生成器 ，遍历一下就都出来了
        items = doc('.news-box .news-list li .txt-box h3 a').items()
        for item in items:
            url = item.attr('href')
            weixin_request = Weixin_Request(url=url, callback=self.parse_detail)
            yield weixin_request
        if self.page <= 100:
            self.page +=1
            url = self.parse_html()
            weixin_request = Weixin_Request(url=url, callback=self.parse_detail, need_proxy=True)
            yield weixin_request





#  parse detail page
    def parse_detail(self, response):
        doc = pq(response.text)
        data = {
            'title':doc('.rich_media_title').text(),
            'cotent':doc('.rich_media_content ').text(),
            'data':doc('#publish_time').text(),#  发布日期
            'nickname':doc('#js_profile_qrcode').text(),
            'wechat':doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        }
        yield data


#  Go
    def run(self):
        self.start()
        self.schedule()


if __name__ == '__main__':
    spider = Spider()
    spider.run()