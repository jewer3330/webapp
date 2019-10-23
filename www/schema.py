from orm import *
import sqlutil 
import asyncio
import config
loop = asyncio.get_event_loop()



async def set_database():
    await sqlutil.create(loop,**config.configs['db'])
    u = User()
    sql = u.__drop__
    await sqlutil.execute(sql,None)
    sql = u.__create__
    await sqlutil.execute(sql,None)

    b = Blog()
    sql = b.__drop__
    await sqlutil.execute(sql,None)
    sql = b.__create__
    await sqlutil.execute(sql,None)
    
    c = Comment()
    sql = c.__drop__
    await sqlutil.execute(sql,None)
    sql = c.__create__
    await sqlutil.execute(sql,None)
    
    d = Link()
    sql = d.__drop__
    await sqlutil.execute(sql,None)
    sql = d.__create__
    await sqlutil.execute(sql,None)

    e = Score()
    sql = e.__drop__
    await sqlutil.execute(sql,None)
    sql = e.__create__
    await sqlutil.execute(sql,None)

    s = Shop()
    sql = s.__drop__
    await sqlutil.execute(sql,None)
    sql = s.__create__
    await sqlutil.execute(sql,None)
    
    event = Event()
    sql = event.__drop__
    await sqlutil.execute(sql,None)
    sql = event.__create__
    await sqlutil.execute(sql,None)

    await sqlutil.destory()

loop.run_until_complete(set_database())
