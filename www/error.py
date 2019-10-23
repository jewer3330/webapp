import logging
class APIError(Exception):
    """docstring for APIError"""
    def __init__(self, name,value,msg):
        super().__init__()
        self.error = name
        self.data = value
        self.message = msg 
        logging.error('Exception:%s value:%s msg:%s'%(self.error,self.data,self.message))

class APIValueError(Exception):
    """docstring for APIValueError"""
    def __init__(self, value,message=None):
        super().__init__()
        self.value = value
        self.message = message

class APIPermissionError(Exception):
    """docstring for APIValueError"""
    def __init__(self, message=None):
        super().__init__()
        self.message = message

class APIResourceNotFoundError(Exception):
    """docstring for APIValueError"""
    def __init__(self, message=None):
        super().__init__()
        self.message = message     
        