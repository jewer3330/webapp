#import sqlutil,asyncio,os
#from user import User

##################################################### map 高级函数测试
# fields = ['id','name','email','password']
# escaped_fields = list(map(lambda f: '`%s`' % f, fields))
# print(escaped_fields)

############################################ orm 测试
# u = User(name = 'sun.xiaomin',email = 'wujiezhaojun@126.com',passwd='zj910421!')
# u.save()
# print(u.id)
# print(u.name)
# print(u.email)
# print(u.image)
# print(u.passwd)
# print(u.created_at)
# print(u.admin)
# print(u.__mappings__)
# print(u.__primary_key__)
# print(u.__table__)
# print(u.__fields__)
# print(u.__select__)
# print(u.__insert__)
# print(u.__update__)
# print(u.__delete__)
# print(dir(u))

############################################# 异步测试
# loop = asyncio.get_event_loop()
# data={
# 	'host':'localhost',
# 	'port':3306,
# 	'user':'root',
# 	'password':'zj910421!',
# 	'db':'test'
# }
# async def user():
#     # u = User(id = 1,name = 'sun.xiaomin',email = 'wujiezhaojun@126.com',passwd='zj910421!')
#     # await u.save()
#     u = await User.findAll("email=?",['wujiezhaojun@126.com'])
#     print(u)
# loop.run_until_complete(sqlutil.create(loop,**data))
# loop.run_until_complete(user())
# loop.run_until_complete(sqlutil.destory())
# loop.close()

##################################################__call__ 测试
# class abc(object):
#     """docstring for abc"""
#     def __init__(self, arg):
#         super(abc, self).__init__()
#         self.arg = arg
#     def __call__(self):
#         print(self.arg)
# abc(1)()

################################################ @ 测试
# def a(arg):
#     print("a func " + arg.__name__)
# #据猜测会把b经过a执行后赋值给b,所以如果a没有返回函数，b就变成了None,猜测成立
# @a
# def b():
#     pass
# print(b)

################################################# inspect
# import inspect
# def a(a, b=0, *c, d, e=1, **f):
#     pass
# aa = inspect.signature(a)
# print("inspect.signature（fn)是:%s" % aa)
# print("inspect.signature（fn)的类型：%s" % (type(aa)))
# print("\n")

# bb = aa.parameters
# print("signature.paramerters属性是:%s" % bb)
# print("ignature.paramerters属性的类型是%s" % type(bb))
# print("\n")

# for cc, dd in bb.items():
#     print("mappingproxy.items()返回的两个值分别是：%s和%s" % (cc, dd))
#     print("mappingproxy.items()返回的两个值的类型分别是：%s和%s" % (type(cc), type(dd)))
#     print("\n")
#     ee = dd.kind
#     print("Parameter.kind属性是:%s" % ee)
#     print("Parameter.kind属性的类型是:%s" % type(ee))
#     print("\n")
#     gg = dd.default
#     print("Parameter.default的值是: %s" % gg)
#     print("Parameter.default的属性是: %s" % type(gg))
#     print("\n")


# ff = inspect.Parameter.KEYWORD_ONLY
# print("inspect.Parameter.KEYWORD_ONLY的值是:%s" % ff)
# print("inspect.Parameter.KEYWORD_ONLY的类型是:%s" % type(ff))

############################### 模块导入测试
## __import__(name[, globals[, locals[, fromlist[, level]]]])
## Python rfind() 返回字符串最后一次出现的位置，如果没有匹配项则返回-1。
# def add_routes(app, module_name):

#     # u =User(name='jun.zhao')
#     # print(getattr(u,"__mappings__"))
#     n = module_name.rfind('.')
#     if n == (-1):
#         mod = __import__(module_name, globals(), locals())
#     else:
#         name = module_name[n+1:]
#         print(name)
#         print(module_name[:n])
#         mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
#     for attr in dir(mod):
#         if attr.startswith('_'):
#             continue
#         fn = getattr(mod, attr)
#         if callable(fn):
#             print(fn)
#             #print(fn.__method__)
#             #print(fn.__route__)

# # add_routes(None,'asyncio')
# add_routes(None,'asyncio.events')


##################################### __file__
# print(__file__)
# path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
# print(path)


################################### test
# def function(i):
#     a = {}
#     if i == 0 :
#         a[i] = i
#         return a
#     else:
#         return function(i = i - 1)

# def function(i,a):
#     if i == 0 :
#         a[i] = i
#         print(a)
#     else:
#         print('_________________')
#         function(i - 1,a)

# print(function(10,{}))


#######################################__dict__
# a = {
#     '1':1,
#     '2':2
# }
# print(a.__dict__)
###############################################
# from urllib import parse
# qs = 'a=b&&c=a'
# print(parse.parse_qs(qs, True))
import time
print(int(time.time()))
stamp = int(time.time())
print(stamp)

today = int(stamp / 3600 / 24) * 24 * 3600 - 8 * 3600
end = today + 24 * 3600 - 1
print(today)
print(end)