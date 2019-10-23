from model import Model,IntegerField,StringField,BooleanField,FloatField,next_id,TextField
import time

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)

class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    passwdtmp = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)
    login_at = FloatField(default=time.time)
    coin = IntegerField(default = 0)
    skin = IntegerField(default = 1)
    device = StringField(ddl='varchar(500)')

class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)

class Link(Model):
    __table__ = 'links'
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    url =  StringField(ddl='varchar(500)')

class Score(Model):
    __table__ = 'scores'
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    score =  IntegerField()
    skin =  IntegerField(default = 1)

class Shop(Model):
    __table__ = 'shops'
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    item1 =  IntegerField(default = 1)
    item2 =  IntegerField(default = 0)
    item3 =  IntegerField(default = 0)
    item4 =  IntegerField(default = 0)
    item5 =  IntegerField(default = 0)
    item6 =  IntegerField(default = 0)
    item7 =  IntegerField(default = 0)
    item8 =  IntegerField(default = 0)
    item9 =  IntegerField(default = 0)
    item10 =  IntegerField(default = 0)
    item11 =  IntegerField(default = 0)
    item12 =  IntegerField(default = 0)
    item13 =  IntegerField(default = 0)
    item14 =  IntegerField(default = 0)
    item15 =  IntegerField(default = 0)
    item16 =  IntegerField(default = 0)
    item17 =  IntegerField(default = 0)
    item18 =  IntegerField(default = 0)
    item19 =  IntegerField(default = 0)
    item20 =  IntegerField(default = 0)
    item21 =  IntegerField(default = 0)
    item22 =  IntegerField(default = 0)

class Event(Model):
    __table__ = "events"
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    time = FloatField(default=time.time)
    isNew = BooleanField()
