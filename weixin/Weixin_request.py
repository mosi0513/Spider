from requests import Request
from config import *
class Weixin_Request(Request):
    #  Add four param(参数)
    def __init__(self, url, callback, method='GET', headers=None, need_proxy=False, fail_time=0,timeout=TIMEOUT):
        Request.__init__(self, method, url, headers)
        self.callback = callback
        self.need_proxy = need_proxy
        self.fail_time = fail_time
        self.timeout = timeout





