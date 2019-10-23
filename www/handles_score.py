import framework,time,re,json,markdown2,const,hashlib,logging,func_email
from aiohttp import web 
from orm import *
from error import APIError,APIValueError,APIPermissionError,APIResourceNotFoundError
from model import next_id
from api import Page,get_page_index,pagination,user2cookie,check_user,text2html,check_admin
logging.basicConfig(level=logging.INFO)

@framework.get('/manage/scores')
def manage_scores(*, page='1'):
	return {
		'__template__': 'admin/manage_scores.html',
		'page_index': get_page_index(page),
		'page_name':'scores'
		
	}

@framework.get('/api/scores')
async def api_scores(*, page='1'):
	page_index = get_page_index(page)
	num = await Score.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, scores=())
	scores = await Score.findAll(orderBy='score desc',limit=(p.offset, p.limit))
	return dict(page=p, scores=scores)

@framework.get('/api/scores/{id}')
async def api_get_score(*, id):
	score = await Score.find(id)
	return score

@framework.post('/api/get_high_score')
async def api_get_high_score(*, uid):
	user = await User.find(uid)
	if user == None:
		raise APIValueError('uid', 'uid not exist.')
	scores = await Score.findAll('user_id=?', [uid])
	score = None
	if len(scores) == 0:
		score = Score(id = next_id(),user_id = user.id,user_name = user.name,user_image = user.image,score = 0,skin = user.skin)
		await score.save()
	else:
		score = scores[0]
		score.skin = user.skin

	return score

@framework.post('/api/scores/update')
async def add_scores(request,*,uid,score_point):
	if uid == None :
		raise APIValueError('uid',"empty")
	if score_point == None or not score_point.isdigit():
		raise APIValueError('score_point','empty')
	user = await User.find(uid)
	if user == None:
		raise APIValueError('uid', 'uid not exist.')
	scores = await Score.findAll('user_id=?', [uid])
	score = None
	if len(scores) == 0:
		score = Score(id = next_id(),user_id = user.id,user_name = user.name,user_image = user.image,score = score_point,skin = user.skin)
		await score.save()
	else:
		score = scores[0]
		score.skin = user.skin
		logging.info(score.skin)
		if int(score_point) > score.score:
			score.score = score_point
		await score.update()			
	return score


@framework.post('/api/scores/{id}/delete')
async def api_delete_score(id,request):
	check_admin(request)
	score = await Score.find(id)
	await score.remove()
	return dict(id=id)


@framework.get('/manage/scores/create')
def manage_create_score():
	return {
		'__template__': 'admin/manage_score_edit.html',
		'id': '',
		'action': '/api/scores/update'
	}

@framework.get('/manage/scores/edit')
def manage_edit_score(*, id):
	return {
		'__template__': 'admin/manage_score_edit.html',
		'id': id,
		'action': '/api/scores/update'
	}