#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging,functools,asyncio,inspect,sqlutil,os,config,time,json,const,hashlib,markdown2
from datetime import datetime
from aiohttp import web 
from jinja2 import Environment, FileSystemLoader
from framework import RequestHandler
from orm import User
import func_email

logging.basicConfig(level=logging.INFO)

def add_route(app, func):
	method = getattr(func, '__method__', None)
	path = getattr(func, '__route__', None)
	if path is None or method is None:
		logging.error('@get or @post not defined in %s.' % str(func))
		return
	##这段函数直接把非异步函数转成异步函数了可以的
	if not asyncio.iscoroutinefunction(func) and not inspect.isgeneratorfunction(func):
		func = asyncio.coroutine(func)
	logging.info('add route %s %s => %s(%s)' % (method, path, func.__name__, ', '.join(inspect.signature(func).parameters.keys())))
	app.router.add_route(method, path, RequestHandler(app, func))

def add_routes(app, module_name):
	n = module_name.rfind('.')
	if n == (-1):
		mod = __import__(module_name, globals(), locals())
	else:
		name = module_name[n+1:]
		mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
	for attr in dir(mod):
		if attr.startswith('_'):
			continue
		func = getattr(mod, attr)
		if callable(func):
			add_route(app,func)

def datetime_filter(t):
	delta = int(time.time() - t)
	if delta < 60:
		return u'1分钟前'
	if delta < 3600:
		return u'%s分钟前' % (delta // 60)
	if delta < 86400:
		return u'%s小时前' % (delta // 3600)
	if delta < 604800:
		return u'%s天前' % (delta // 86400)
	dt = datetime.fromtimestamp(t)
	return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)

def init_jinja2(app, **kw):
	logging.info('init jinja2...')
	options = dict(
		autoescape = kw.get('autoescape', True),
		block_start_string = kw.get('block_start_string', '{%'),
		block_end_string = kw.get('block_end_string', '%}'),
		variable_start_string = kw.get('variable_start_string', '(('),
		variable_end_string = kw.get('variable_end_string', '))'),
		auto_reload = kw.get('auto_reload', True)
	)
	path = kw.get('path', None)
	if path is None:
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
		logging.info('set jinja2 template path: %s' % path)
		env = Environment(loader=FileSystemLoader(path), **options)
	
		filters = kw.get('filters', None)
		if filters is not None:
			for name, f in filters.items():
				env.filters[name] = f
			app['__templating__'] = env

#返回一个处理的函数，有点像责任链模式
async def logger_factory(app, handler):
	async def logger(request):
		logging.info('Request: %s %s' % (request.method, request.path))
		# print(handler)
		return (await handler(request))
	return logger

async def response_factory(app, handler):
	async def response(request):
		logging.info('Response handler...')
		r = await handler(request)
		
		if isinstance(r, web.StreamResponse):
			logging.info("r is web.StreamResponse")
			return r
		if isinstance(r, bytes):
			logging.info("r bytes")
			resp = web.Response(body=r)
			resp.content_type = 'application/octet-stream'
			return resp

		if isinstance(r, str):
			if r.startswith('redirect:'):
				logging.info("r is redirect")
				return web.HTTPFound(r[9:])
			else:
				logging.info("r is string")
				resp = web.Response(body=r.encode('utf-8'))
				resp.content_type = 'text/html;charset=utf-8'
				return resp

		if isinstance(r, dict):
			logging.info("r is dict")
			template = r.get('__template__')

			if template is None:
				logging.info("template is None")

				resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
				resp.content_type = 'application/json;charset=utf-8'
				return resp
			else:
				logging.info("renader template")
				if request.__user__ is not None:
					r['__user__'] = request.__user__
				resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
				resp.content_type = 'text/html;charset=utf-8'
				return resp

		if isinstance(r, int) and r >= 100 and r < 600:
			return web.Response(r)
		
		if isinstance(r, tuple) and len(r) == 2:
			t, m = r
			if isinstance(t, int) and t >= 100 and t < 600:
				return web.Response(t, str(m))
		
		# default:
		resp = web.Response(body=str(r).encode('utf-8'))
		resp.content_type = 'text/plain;charset=utf-8'
		return resp
	return response

def add_static(app):
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
	app.router.add_static('/static/', path)
	logging.info('add static %s => %s' % ('/static/', path))


async def auth_factory(app, handler):
   
	async def auth(request):
		logging.info('check user: %s %s' % (request.method, request.path))
		request.__user__ = None
		cookie_str = request.cookies.get(const._COOKIE_NAME)
		if cookie_str:
			user = await cookie2user(cookie_str)
			if user:
				logging.info('set current user: %s' % user.email)
				request.__user__ = user
		if request.path.startswith('/manage/') and (request.__user__ is None or not request.__user__.admin):
			return web.HTTPFound('/signin')
		return (await handler(request))
	return auth

# 解密cookie:
async def cookie2user(cookie_str):
	'''
	Parse cookie and load user if cookie is valid.
	'''
	if not cookie_str:
		return None
	try:
		L = cookie_str.split('-')
		if len(L) != 3:
			return None
		uid, expires, sha1 = L
		if int(expires) < time.time():
			return None
		user = await User.find(uid)
		if user is None:
			return None
		s = '%s-%s-%s-%s' % (uid, user.passwd, expires, const._COOKIE_KEY)
		if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
			logging.info('invalid sha1')
			return None
		user.passwd = '******'
		return user
	except Exception as e:
		logging.exception(e)
		return None

async def init(loop):
	# app = web.Application(loop=loop)
	await sqlutil.create(loop,**config.configs['db'])
	app = web.Application(loop=loop,middlewares = [logger_factory,auth_factory,response_factory])
	add_routes(app,'handles')
	add_routes(app,'handles_score')
	add_routes(app,'handles_shop')
	add_routes(app,'handles_event')
	init_jinja2(app, filters=dict(datetime=datetime_filter))
	add_static(app)
	func_email._init_email_template()
	srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8000)
	logging.info('Server started at http://127.0.0.1:8000...')
	return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()



