import logging,asyncio,aiomysql
logging.basicConfig(level=logging.INFO)

async def create(loop,**kw):
	logging.info("create %s"%(kw))
	global __pool
	__pool = await aiomysql.create_pool(
		host = kw.get('host','localhost'),
		port = kw.get('port','3306'),
		user = kw['user'],
		password = kw['password'],
		db = kw['db'],
		charset = kw.get('charset','utf8'),
		autocommit = kw.get('autocommit',True),
		maxsize = kw.get('maxsize',10),
		minsize = kw.get('minsize',1),
		loop = loop
		)

async def select(sql,args,size = None):
	logging.info("select %s %s" %(sql,str(args)))
	global __pool
	async with __pool.get()  as conn:
		async with conn.cursor(aiomysql.DictCursor) as cur:
			await cur.execute(sql.replace('?','%s'),args or ())
			if size :
				rs = await cur.fetchmany(size)
			else:
				rs = await cur.fetchall()
			logging.info("rows %s"%(len(rs)))
			return rs

async def execute(sql,args):
	logging.info("execute %s %s" %(sql,str(args)))
	global __pool
	async with __pool.get()  as conn:
		async with conn.cursor(aiomysql.DictCursor) as cur:
			cur = await conn.cursor(aiomysql.DictCursor)
			await cur.execute(sql.replace('?','%s'),args or ())
			affected = cur.rowcount
			logging.info("rows %s"%(affected))
			return affected


async def destory():
    global __pool
    if __pool is not None:
        __pool.close()
        await __pool.wait_closed()

