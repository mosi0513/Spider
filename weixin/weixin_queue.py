from pickle import dumps, loads
from Weixin_request import Weixin_Request
from config import *
from redis import StrictRedis

#  create object /// redis queue

class RedisQueue(object):

    def __init__(self):
        #  host 主机   #  port端口    #password密码
        #  初始化方法   #  StricRedis是执行redis命令的方法
        self.db = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

    #  add object
    def add(self,request):
        #  如果传入的request类型是Weixin_Request类型，布尔值为真
        if isinstance(request,Weixin_Request):
            #  如果条件为真，则返回条件，且添加到队列
            return self.db.rpush(REDIS_KEY, dumps(request))
        return False
    #  pop object
    def pop(self):
        if self.db.llen(REDIS_KEY):#  如果队列长度为真（有东西则为真，没东西为空，则为假)
            return loads(self.db.lpop(REDIS_KEY))
        else:
            return False
    #  ///为调度的时候写一个条件
    def empty(self):
        return self.db.llen(REDIS_KEY) == 0
