import framework,time,re,json,markdown2,const,hashlib,logging,func_email,math
import datetime
from aiohttp import web 
from orm import *
from const import *
from error import APIError,APIValueError,APIPermissionError,APIResourceNotFoundError
from model import next_id
from api import Page,get_page_index,pagination,user2cookie,check_user,text2html,check_admin
logging.basicConfig(level=logging.INFO)

def _get_day_start_timestamp(stamp):
	today = int(stamp / 3600 / 24) * 24 * 3600 - 8 * 3600
	return today

def _get_day_end_timestamp(stamp):
	today = int(stamp / 3600 / 24) * 24 * 3600 + 16 * 3600 - 1
	return today


@framework.get('/manage/events')
def manage_events(*, page='1'):
	return {
		'__template__': 'admin/manage_events.html',
		'page_index': get_page_index(page),
		'page_name':'events'
	}

@framework.get('/api/active_users')
async def api_active_users(*, deltaDay = 7,today = time.time()):
	if deltaDay == None:
		raise APIValueError('deltaDay','empty')
	if today == None:
		raise APIValueError('today','empty')
	deltaDay = int(deltaDay)

	labels = []
	series = []
	series1 = []
	
	start_timestamp = int(today) - deltaDay * 24 *3600
	
	for x in range(0,deltaDay + 1):
		t = start_timestamp + x * 24 * 3600
		
		s_from = _get_day_start_timestamp(t)
		s_end = _get_day_end_timestamp(t)
		labels.append( s_from)
		events = await Event.findAll('time>=? and time<=? and name="auth" group by user_id', [s_from,s_end])
		series1.append(len(events))			
	series.append(series1)
	return dict(labels=labels,series=series);




@framework.get('/api/reg_users')
async def api_reg_users(*, deltaDay = 7,today =  time.time()):
	if deltaDay == None :
		raise APIValueError('deltaDay','empty')
	if today == None :
		raise APIValueError('today','empty')
	deltaDay = int(deltaDay)

	labels = []
	series = []
	series1 = []
	start_timestamp = int(today) - deltaDay * 24 *3600
	
	for x in range(0,deltaDay + 1):
		t = start_timestamp + x * 24 * 3600
		
		s_from = _get_day_start_timestamp(t)
		s_end = _get_day_end_timestamp(t)
		labels.append( s_from)
		
		events = await Event.findAll('time>=? and time<= ? and name="auth" and isNew=true group by user_id', [s_from,s_end])
		series1.append(len(events))
	series.append(series1)
	return dict(labels=labels,series=series);

@framework.get('/api/day_keep')
async def api_day_keep(*,daykeep = 1,today =time.time() ):
	if daykeep == None :
		raise APIValueError('daykeep','empty')
	if today == None :
		raise APIValueError('today','empty')
	daykeep = int(daykeep)
	day = int(today)
	
	date_from_stamp = _get_day_start_timestamp(day)
	date_to_stamp = _get_day_end_timestamp(day)

	nextday = day + daykeep * 24 *3600
	
	next_date_from_stamp = _get_day_start_timestamp(nextday)
	next_date_to_stamp = _get_day_end_timestamp(nextday)

	events_reg = await Event.findAll('time>=? and time<= ? and name="auth" and isNew=true group by user_id', [date_from_stamp,date_to_stamp])
	events_auth = await Event.findAll('user_id in (select user_id from events where time >= ? and time <= ? and name = "auth" and isNew = false) and time>=? and time<= ? and name="auth" and isNew=true group by user_id', [next_date_from_stamp,next_date_to_stamp,date_from_stamp,date_to_stamp])

	if len(events_reg) == 0 :
		return 0.0
	return len(events_auth) / len(events_reg)

@framework.get('/api/one_day_keep')
async def api_one_day_keep(*, deltaDay = 7,today =  time.time()):
	ret = await day_keep(1,deltaDay,today)
	return ret;

async def day_keep(daykeep = 1,deltaDay = 7,today = time.time()):
	if deltaDay == None :
		raise APIValueError('deltaDay','empty')
	if today == None :
		raise APIValueError('today','empty')
	deltaDay = int(deltaDay)

	labels = []
	series = []
	series1 = []
	start_timestamp = int(today) - deltaDay * 24 *3600

	
	for x in range(0,deltaDay + 1):
		
		t = start_timestamp + x * 24 * 3600
		s_from = _get_day_start_timestamp(t)
		s_end = _get_day_end_timestamp(t)
		labels.append( s_from)

		events = await api_day_keep(daykeep = daykeep,today = s_end)
		series1.append(events)
	series.append(series1)
	return dict(labels=labels,series=series);

@framework.get('/api/two_day_keep')
async def api_two_day_keep(*, deltaDay = 7,today =  time.time()):
	ret = await day_keep(2,deltaDay,today)
	return ret;

@framework.get('/api/three_day_keep')
async def api_three_day_keep(*, deltaDay = 7,today =  time.time()):
	ret = await day_keep(3,deltaDay,today)
	return ret;

@framework.get('/api/seven_day_keep')
async def api_seven_day_keep(*, deltaDay = 7,today =  time.time()):
	ret = await day_keep(7,deltaDay,today)
	return ret;