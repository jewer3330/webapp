import framework,time,re,json,markdown2,const,hashlib,logging,func_email
from aiohttp import web 
from orm import *
from error import APIError,APIValueError,APIPermissionError,APIResourceNotFoundError
from model import next_id
from api import Page,get_page_index,pagination,user2cookie,check_user,text2html,check_admin
logging.basicConfig(level=logging.INFO)

@framework.get('/manage/shops')
def manage_shops(*, page='1'):
	return {
		'__template__': 'admin/manage_shops.html',
		'page_index': get_page_index(page),
		'page_name':'shops'
		
	}

@framework.get('/api/shops')
async def api_shops(*, page='1'):
	page_index = get_page_index(page)
	num = await Shop.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, shops=())
	shops = await Shop.findAll(limit=(p.offset, p.limit))
	return dict(page=p, shops=shops)

@framework.get('/api/shops/{id}')
async def api_get_shop(*, id):
	shop = await Shop.find(id)
	return shop

@framework.post('/api/shop')
async def api_shop(*, uid):
	user = await User.find(uid)
	if user == None:
		raise APIValueError('uid', 'uid not exist.')
	shops = await Shop.findAll('user_id=?', [uid])
	shop = None
	if len(shops) == 0:
		shop = Shop(id = next_id(),user_id = user.id,user_name = user.name,user_image = user.image)
		await shop.save()
	else:
		shop = shops[0]
	return shop



@framework.post('/api/shops/update')
async def api_shops_update(*,uid,item1,item2,item3,item4,item5,item6,item7):
	if uid == None :
		raise APIValueError('uid',"empty")
	if item1 == None or not item1.isdigit():
		raise APIValueError('item1','empty')
	if item2 == None or not item2.isdigit():
		raise APIValueError('item2','empty')
	if item3 == None or not item3.isdigit():
		raise APIValueError('item3','empty')
	if item4 == None or not item4.isdigit():
		raise APIValueError('item4','empty')
	if item5 == None or not item5.isdigit():
		raise APIValueError('item5','empty')
	if item6 == None or not item6.isdigit():
		raise APIValueError('item6','empty')
	if item7 == None or not item7.isdigit():
		raise APIValueError('item7','empty')
		
	user = await User.find(uid)
	if user == None:
		raise APIValueError('uid', 'uid not exist.')
	shops = await Shop.findAll('user_id=?', [uid])
	shop = None
	if len(shops) == 0:
		shop = Shop(id = next_id(),user_id = user.id,user_name = user.name,user_image = user.image,
			item1 = item1,item2 = item2,item3 = item3,item4 = item4,item5 = item5,item6 = item6,item7 = item7)
		await shop.save()
	else:
		shop = shops[0]
		shop.item1 = item1
		shop.item2 = item2
		shop.item3 = item3
		shop.item4 = item4
		shop.item5 = item5
		shop.item6 = item6
		shop.item7 = item7
		await shop.update()			
	return shop


@framework.post('/api/shops/buy')
async def add_shops(*,uid,index):
	if uid == None :
		raise APIValueError('uid',"empty")
	if index == None or not index.isdigit():
		raise APIValueError('index','empty')
	if int(index) <= 0 or int(index) >= 23:
		raise APIValueError('index','invalid')		
	key = "item" + index

		
	user = await User.find(uid)
	if user == None:
		raise APIValueError('uid', 'uid not exist.')
	shops = await Shop.findAll('user_id=?', [uid])
	shop = None
	if len(shops) == 0:
		shop = Shop(id = next_id(),user_id = user.id,user_name = user.name,user_image = user.image,
			key = 1)
		await shop.save()
	else:
		shop = shops[0]
		shop[key] = 1
		await shop.update()			
	return shop



@framework.post('/api/shops/{id}/delete')
async def api_delete_shop(id,request):
	check_admin(request)
	shop = await Shop.find(id)
	await shop.remove()
	return dict(id=id)


@framework.get('/manage/shops/create')
def manage_create_shop():
	return {
		'__template__': 'admin/manage_shop_edit.html',
		'id': '',
		'action': '/api/shops/update'
	}

@framework.get('/manage/shops/edit')
def manage_edit_shop(*, id):
	return {
		'__template__': 'admin/manage_shop_edit.html',
		'id': id,
		'action': '/api/shops/update'
	}
