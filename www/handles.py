import framework,time,re,json,markdown2,const,hashlib,logging,func_email
from aiohttp import web 
from orm import *
from error import APIError,APIValueError,APIPermissionError,APIResourceNotFoundError
from model import next_id
from api import Page,get_page_index,pagination,user2cookie,check_user,text2html,check_admin
logging.basicConfig(level=logging.INFO)


@framework.get('/reg')
async def register():
	links = await Link.findAll()
	return {
		'__template__': 'reg.html',
		'links': links,
		'page_name' : 'reg'
		

	}

@framework.get('/signin')
async def signin():
	links = await Link.findAll()
	return {
		'__template__': 'signin.html',
		'links': links,
		'page_name' : 'signin'

	}

@framework.get('/services')
async def services():
	links = await Link.findAll()
	return {
		'__template__': 'services.html',
		'links': links,
		'page_name' : 'services'
	}

@framework.get('/privacy')
async def privacy():
	links = await Link.findAll()
	return {
		'__template__': 'privacy.html',
		'links': links,
		'page_name' : 'privacy'
	}

@framework.get('/about')
async def about():
	links = await Link.findAll()
	return {
		'__template__': 'about.html',
		'links': links,
		'page_name' : 'about'
	}

@framework.get('/contact')
async def contact():
	links = await Link.findAll()
	return {
		'__template__': 'contact.html',
		'links': links,
		'page_name' : 'contact'
	}

@framework.get('/')
async def index(*, page='1'):
	page_index = get_page_index(page)
	num = await Blog.findNumber('count(id)')
	page = Page(num,page_index)
	print(page)
	if num == 0:
		blogs = []
	else:
		blogs = await Blog.findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
	links = await Link.findAll()
	return {
		'__template__': 'blogs.html',
		'page': page,
		'blogs': blogs,
		'links': links,
		'page_name' : 'index'
	}

@framework.get('/blog/{id}')
async def get_blog(id):
	blog = await Blog.find(id)
	blog.html_content = markdown2.markdown(blog.content)
	comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
	for c in comments:
		c.html_content = text2html(c.content)
	links = await Link.findAll()
	return {
		'__template__': 'blog.html',
		'blog': blog,
		'links': links,
		'comments': comments
	}




@framework.get('/manage/')
def manage():
	return 'redirect:/manage/blogs'

@framework.get('/manage/comments')
def manage_comments(*, page='1'):
	return {
		'__template__': 'admin/manage_comments.html',
		'page_index': get_page_index(page),
		'page_name':'comments'
	}

@framework.get('/manage/blogs')
def manage_blogs(*, page='1'):
	return {
		'__template__': 'admin/manage_blogs.html',
		'page_index': get_page_index(page),
		'page_name':'blogs'
	}



@framework.get('/manage/blogs/create')
def manage_create_blog():
	return {
		'__template__': 'admin/manage_blog_edit.html',
		'id': '',
		'action': '/api/blogs/add'
	}

@framework.get('/manage/blogs/edit')
def manage_edit_blog(*, id):
	return {
		'__template__': 'admin/manage_blog_edit.html',
		'id': id,
		'action': '/api/blogs/%s' % id
	}

@framework.get('/manage/users')
def manage_users(*, page='1'):
	return {
		'__template__': 'admin/manage_users.html',
		'page_index': get_page_index(page),
		'page_name':'users'
	}


@framework.get('/api/comments')
async def api_comments(*, page='1'):
	page_index = get_page_index(page)
	num = await Comment.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, comments=())
	comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	return dict(page=p, comments=comments)

@framework.post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, content):
	user = request.__user__
	if user is None:
		raise APIPermissionError('Please signin first.')
	if not content or not content.strip():
		raise APIValueError('content')
	blog = await Blog.find(id)
	if blog is None:
		raise APIResourceNotFoundError('Blog')
	comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
	await comment.save()
	return comment

@framework.post('/api/comments/{id}/delete')
async def api_delete_comments(id, request):
	check_admin(request)
	c = await Comment.find(id)
	if c is None:
		raise APIResourceNotFoundError('Comment')
	await c.remove()
	return dict(id=id)

@framework.get('/api/user')
def api_get_cookie_user(request):
	user = request.__user__
	user.passwd = '******'
	return user

@framework.get('/api/users')
async def api_get_users(*, page='1'):
	page_index = get_page_index(page)
	num = await User.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, users=())
	users = await User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	for u in users:
		u.passwd = '******'
	return dict(page=p, users=users)

@framework.post('/api/find_user')
async def api_find_user(*, uid):
	user = await User.find(uid)
	if user == None:
		raise APIValueError('user',"not find")
	user.passwd = '******'
	return user	

@framework.post('/api/update/coin')
async def api_update_coin(*, uid,coin):
	user = await User.find(uid)
	if user == None:
		raise APIValueError('user',"not find")
	if coin == None or not coin.isdigit():
		raise APIValueError('coin',"empty")
	user.coin = coin
	await user.update()
	user.passwd = '******'
	return user	

@framework.post('/api/update/skin')
async def api_update_skin(*, uid,skin):
	user = await User.find(uid)
	if user == None:
		raise APIValueError('user',"not find")
	if skin == None or not skin.isdigit():
		raise APIValueError('skin',"empty")
	user.skin = skin
	await user.update()
	user.passwd = '******'
	return user	

@framework.get('/api/blogs')
async def api_blogs(*, page='1'):
	page_index = get_page_index(page)
	num = await Blog.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, blogs=())
	blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
	return dict(page=p, blogs=blogs)

@framework.get('/api/blogs/{id}')
async def api_get_blog(*, id):
	blog = await Blog.find(id)
	return blog

@framework.post('/api/blogs/add')
async def add_blogs(request,*,name,summary,content):
	check_admin(request)
	if name == None :
		raise APIValueError('name',"empty")
	if summary == None:
		raise APIValueError('summary','empty')
	if content == None:
		raise APIValueError('content','empty')
	b = Blog(id = next_id(),name = name,summary = summary,content= content,created_at= time.time()
		,user_id =request.__user__.id,user_name= request.__user__.name,user_image= request.__user__.image)
	await b.save()
	return b

@framework.post('/api/blogs/{id}')
async def api_update_blog(id, request, *, name, summary, content):
	check_admin(request)
	blog = await Blog.find(id)
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty.')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty.')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty.')
	blog.name = name.strip()
	blog.summary = summary.strip()
	blog.content = content.strip()
	await blog.update()
	return blog

@framework.post('/api/blogs/{id}/delete')
async def api_delete_blog(id,request):
	check_admin(request)
	blog = await Blog.find(id)
	await blog.remove()
	return dict(id=id)

@framework.post('/api/reg')
async def api_register_user(*, email, name, passwd):
	if not name or not name.strip():
		raise APIValueError('name')
	if not email or not const._RE_EMAIL.match(email):
		raise APIValueError('email')
	if not passwd or not const._RE_SHA1.match(passwd):
		raise APIValueError('passwd')
	users = await User.findAll('email=?', [email])
	if len(users) > 0:
		raise APIValueError('email', 'Email is already in use.')
	uid = next_id()
	sha1_passwd = '%s:%s' % (uid, passwd)
	user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='https://www.gravatar.com/avatar/%s?d=wavatar&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
	await user.save()
	event = Event(name = "auth",user_id = user.id,isNew = True)
	await event.save()
	# make session cookie:
	r = web.Response()
	r.set_cookie(const._COOKIE_NAME, user2cookie(user, 3600), max_age=3600, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r

@framework.post('/api/auth')
async def authenticate(*, email, passwd):
	logging.info('use email {0},passwd {1}'.format(email,passwd))
	if not email:
		raise APIValueError('email', 'Invalid email.')
	if not passwd:
		raise APIValueError('passwd', 'Invalid password.')
	users = await User.findAll('email=?', [email])
	if len(users) == 0:
		raise APIValueError('email', 'The account does not exist, please register')
	user = users[0]
	# check passwd:
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	sha1.update(passwd.encode('utf-8'))
	if user.passwd != sha1.hexdigest():
		raise APIValueError('passwd', 'Invalid password.')

	
	event = Event(name = "auth",user_id = user.id,isNew = False)
	await event.save()
	# authenticate ok, set cookie:
	r = web.Response()
	r.set_cookie(const._COOKIE_NAME, user2cookie(user, 3600), max_age=3600, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r

@framework.post('/api/login_with_device')
async def login_with_device(*, device):
	logging.info('use login_with_device ')
	if not device:
		raise APIValueError('device', 'Invalid device.')
	users = await User.findAll('device=?', [device])
	user = None
	if len(users) == 0:		
		uid = next_id()
		user = User(id=uid,device=device)
		await user.save()
		event = Event(name = "auth",user_id = user.id,isNew = True)
		await event.save()
	else:
		user = users[0]
		event = Event(name = "auth",user_id = user.id,isNew = False)
		await event.save()

	# authenticate ok, set cookie:
	r = web.Response()
	r.set_cookie(const._COOKIE_NAME, user2cookie(user, 3600), max_age=3600, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r

@framework.post('/api/auth1')
async def authenticate1(*, email, passwd,device):
	logging.info('use email {0},passwd {1}'.format(email,passwd))
	if not email:
		raise APIValueError('email', 'Invalid email.')
	if not passwd:
		raise APIValueError('passwd', 'Invalid password.')
	if not device:
		raise APIValueError('device', 'Invalid device.')
	users = await User.findAll('email=?', [email])
	if len(users) == 0:
		raise APIValueError('email', 'The account does not exist, please register')
	user = users[0]
	# check passwd:
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	sha1.update(passwd.encode('utf-8'))
	if user.passwd != sha1.hexdigest():
		raise APIValueError('passwd', 'Invalid password.')
	if user.device != device:
		user.device = device
		await user.update()

	event = Event(name = "auth",user_id = user.id,isNew = False)
	await event.save()
	# authenticate ok, set cookie:
	r = web.Response()
	r.set_cookie(const._COOKIE_NAME, user2cookie(user, 3600), max_age=3600, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r

@framework.get('/signout')
def signout(request):
	referer = request.headers.get('Referer')
	r = web.HTTPFound(referer or '/')
	r.set_cookie(const._COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
	logging.info('user signed out.')
	return r


@framework.post('/api/req_reset_password')
async def req_reset_password(*, email):
	if not email:
		raise APIValueError('email', 'Invalid email.')
	users = await User.findAll('email=?', [email])
	if len(users) == 0:
		raise APIValueError('email', 'Email not exist.')
	user = users[0]

	tmp = user.email + ':' + str(time.time()) + user.passwd
	
	# check passwd:
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	sha1.update(tmp.encode('utf-8'))
	user.passwdtmp = sha1.hexdigest();
	await user.update()
	#email
	# url /resetpassword?email='%s'&pass='%s'
	func_email._send_reset_password_email(user.name,user.email,"{2}/querypassword?email={0}&key={1}".format(user.email,user.passwdtmp,const._EMAIL_SERVER))
	user.passwd = "*********"
	user.passwdtmp = "*********"

	return user

@framework.get('/resetpassword')
def resetpassword():
	return {
		'__template__': 'resetpassword.html',
	}

@framework.get('/querypassword')
async def query_password(*,email,key):
	if not email:
		return {
			'__template__': 'error.html',
			'message': 'Invalid email.',
		}
		# raise APIValueError('email', 'Invalid email.')
	users = await User.findAll('email=?', [email])
	if len(users) == 0:
		return {
			'__template__': 'error.html',
			'message': 'Email not exist.',
		}
		# raise APIValueError('email', 'Email not exist.')
	user = users[0]

	if user.passwdtmp != key:
		return {
			'__template__': 'error.html',
			'message': 'Invalid reset key.',
		}
		# raise APIValueError('passwd', 'Invalid reset key.')

	
	return {
		'__template__': 'querypassword.html',
		'email': email,
		'passwdtmp' : key
	}


@framework.post('/api/query_reset_password')
async def query_reset_password(*, email,password,passwdtmp):


	if not email:
		raise APIValueError('email', 'Invalid email.')
	users = await User.findAll('email=?', [email])
	if len(users) == 0:
		raise APIValueError('email', 'Email not exist.')
	user = users[0]
	if user.passwdtmp != passwdtmp:
		raise APIValueError('email', 'Invalid reset key.')

	sha1_passwd = '%s:%s' % (user.id, password)
	user.passwd = hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest()
	user.passwdtmp = ''
	await user.update()

	# authenticate ok, set cookie:
	r = web.Response()
	r.set_cookie(const._COOKIE_NAME, user2cookie(user, 3600), max_age=3600, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r


@framework.get('/manage/links')
def manage_links(*, page='1'):
	return {
		'__template__': 'admin/manage_links.html',
		'page_index': get_page_index(page),
		'page_name':'links'
		
	}

@framework.get('/api/links')
async def api_links(*, page='1'):
	page_index = get_page_index(page)
	num = await Link.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, links=())
	links = await Link.findAll(limit=(p.offset, p.limit))
	return dict(page=p, links=links)

@framework.get('/api/links/{id}')
async def api_get_link(*, id):
	link = await Link.find(id)
	return link

@framework.post('/api/links/add')
async def add_links(request,*,name,url):
	check_admin(request)
	if name == None :
		raise APIValueError('name',"empty")
	if url == None:
		raise APIValueError('url','empty')
	b = Link(id = next_id(),name = name,url = url)
	await b.save()
	return b

@framework.post('/api/links/{id}')
async def api_update_link(id, request, *, name, url):
	check_admin(request)
	link = await Link.find(id)
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty.')
	if not url or not url.strip():
		raise APIValueError('url', 'url cannot be empty.')
	link.name = name.strip()
	link.url = url.strip()
	await link.update()
	return link

@framework.post('/api/links/{id}/delete')
async def api_delete_link(id,request):
	check_admin(request)
	link = await Link.find(id)
	await link.remove()
	return dict(id=id)


@framework.get('/manage/links/create')
def manage_create_link():
	return {
		'__template__': 'admin/manage_link_edit.html',
		'id': '',
		'action': '/api/links/add'
	}

@framework.get('/manage/links/edit')
def manage_edit_link(*, id):
	return {
		'__template__': 'admin/manage_link_edit.html',
		'id': id,
		'action': '/api/links/%s' % id
	}