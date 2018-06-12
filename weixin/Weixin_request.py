from requests import Request
from config import *
class Weixin_Request(Request):
    #  Add four param(参数)
    def __init__(self, url, callback, method='GET', headers=None, need_proxy=False, fail_time=0,timeout=TIMEOUT):

        #  上面一行是一些参数
        #  method url headers 会被添加到request方法里面进行求求
        #  __init__ 参数主要是判断外部传入请求的类型 # 例如索引页与详细页不同的方法，可以返回两个不同的对象，方便加入队列进行处理
        #  比如需要代理是一种对象，而不需要代理又是一种对象
        # 执行万之后再把相关的数据传输到下面的Requesrs方法，最后返回给发送的对象

        Request.__init__(self, method, url, headers)

        #  上面一行是请求的方法

        self.callback = callback
        self.need_proxy = need_proxy
        self.fail_time = fail_time
        self.timeout = timeout





