import logging
logging.basicConfig(level=logging.INFO)

import sqlutil 
import time,uuid


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class Field():
	def __init__(self,name,ddl, primary_key,default):
		self.name = name
		self.ddl = ddl
		self.primary_key = primary_key
		self.default = default
		
	def __str__(self):
		s = "<%s:%s>"%(self.__class__.__name__,self.name)
		return s
	

class IntegerField(Field):
	def __init__(self,name=None,default=1,primary_key=False,ddl='bigint'):
		super().__init__(name,ddl,primary_key,default)
		
class StringField(Field):
	def __init__(self,name=None,default='',primary_key=False,ddl='varchar(100)'):
		super().__init__(name,ddl,primary_key,default)

class FloatField(Field):
	def __init__(self,name=None,default=0.0,primary_key=False,ddl='real'):
		super().__init__(name,ddl,primary_key,default)		

class BooleanField(Field):
	def __init__(self,name=None,default=False,primary_key=False,ddl='boolean'):
		super().__init__(name,ddl,primary_key,default)	

class TextField(Field):
	def __init__(self,name=None,default='',primary_key=False,ddl='text'):
		super().__init__(name,ddl,primary_key,default)	

def create_args_string(num):
	L = []
	for n in range(num):
		L.append('?')
	return ', '.join(L)

def create_field_string(primaryKey,fields,mappings):
	primary_s = '`%s` %s not null,'%(primaryKey,mappings.get(primaryKey).ddl)
	str =', '.join(map(lambda f: '`%s` %s not null' % (mappings.get(f).name or f,mappings.get(f).ddl),fields))
	str = primary_s + str + ',primary key (`%s`)'% primaryKey
	# print(str)
	return str

class ModelMetaClass(type):
	def __new__(cls,name,bases,attrs):
		if name == 'Model':
			return type.__new__(cls,name,bases,attrs)
		tableName = attrs.get('__table__', None) or name
		mappings = dict()
		fields = []
		primaryKey = None
		for k,v in attrs.items():
			if isinstance(v,Field):
				mappings[k]=v
				if v.primary_key:	
					if primaryKey:
						logging.error("duplicate key %s"%(k))
						raise RuntimeError('Duplicate primary key for field: %s' % k)
					primaryKey = k
				else:
					fields.append(k)

		for k in mappings.keys():
			attrs.pop(k)
		escaped_fields = list(map(lambda f: '`%s`' % f, fields))
		# print(escaped_fields)
		attrs['__mappings__'] = mappings # 保存属性和列的映射关系
		attrs['__table__'] = tableName
		attrs['__primary_key__'] = primaryKey # 主键属性名
		attrs['__fields__'] = fields # 除主键外的属性名
		# 构造默认的SELECT, INSERT, UPDATE和DELETE语句:
		attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
		attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
		attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
		attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
		attrs['__create__'] = 'create table `%s` (%s) engine = InnoDB default character set = utf8' %(tableName,create_field_string(primaryKey,fields,mappings))
		attrs['__drop__'] = 'drop table if exists `%s`' % tableName

		return type.__new__(cls,name,bases,attrs)

class Model(dict,metaclass = ModelMetaClass):
	def __init__(self, **kw):
		super().__init__(kw)

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			print("%s not find" % key)
	
	def __setattr__(self, key, value):
		self[key] = value

	def getValue(self, key):
		return getattr(self, key, None)

	def getValueOrDefault(self, key):
		value = getattr(self, key, None)
		if value is None:
			field = self.__mappings__[key]
			if field.default is not None:
				value = field.default() if callable(field.default) else field.default
				logging.debug('using default value for %s: %s' % (key, str(value)))
				setattr(self, key, value)
		return value

	async def save(self):
		args = list(map(self.getValueOrDefault, self.__fields__))
		args.append(self.getValueOrDefault(self.__primary_key__))
		rows = await sqlutil.execute(self.__insert__, args)
		if rows != 1:
			logging.warn('failed to insert record: affected rows: %s' % rows)
	
	async def update(self):
		args = list(map(self.getValue, self.__fields__))
		args.append(self.getValue(self.__primary_key__))
		rows = await sqlutil.execute(self.__update__, args)
		if rows != 1:
			logging.warn('failed to update by primary key: affected rows: %s' % rows)

	async def remove(self):
		args = [self.getValue(self.__primary_key__)]
		rows = await sqlutil.execute(self.__delete__, args)
		if rows != 1:
			logging.warn('failed to remove by primary key: affected rows: %s' % rows)

	@classmethod 
	async def findNumber(cls,sql):
		rs = await sqlutil.select('select %s as _num_ from %s'%(sql,cls.__table__),None)
		if len(rs) == 0:
			return None

		return rs[0]['_num_']
			

	@classmethod
	async def find(cls, pk):
		''' find object by primary key. '''
		rs = await sqlutil.select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
		if len(rs) == 0:
			return None
		return cls(**rs[0])

	@classmethod
	async def findAll(cls, where=None, args=None, **kw):
		' find objects by where clause. '
		sql = [cls.__select__]
		if where:
			sql.append('where')
			sql.append(where)
		if args is None:
			args = []
		orderBy = kw.get('orderBy', None)
		if orderBy:
			sql.append('order by')
			sql.append(orderBy)
		limit = kw.get('limit', None)
		if limit is not None:
			sql.append('limit')
			if isinstance(limit, int):
				sql.append('?')
				args.append(limit)
			elif isinstance(limit, tuple) and len(limit) == 2:
				sql.append('?, ?')
				args.extend(limit)
			else:
				raise ValueError('Invalid limit value: %s' % str(limit))
		rs = await sqlutil.select(' '.join(sql), args)
		return [cls(**r) for r in rs]
		