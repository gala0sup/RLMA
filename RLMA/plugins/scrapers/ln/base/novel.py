'''Base class for light novel scrapers'''

import json
import logging

class NotInitializedError(Exception):
    '''when info is called before get_info'''

    def __init__(self,message="info() is called before calling get_info('link')"):
        self.message = message
        super().__init__(self.message)

class about_dict(object):
    def __init__(self):
        self.__dict__ = {
            'CoverImage':None,
            'Name':None,
            'Chapters':None,
            'Author':None,
            'Status':None,
            'Release':None,
            'Updated':None,
            'Summary':None
        }
    def __setitem__(self, key, value):
        if key not in self.__dict__.keys():
            raise KeyError('no New key Allowed')

        self.__dict__[key] = value
        
    def __getitem__(self, key):
        return self.__dict__[key]
    def keys(self):
        return self.__dict__.keys()
        
    def update(self, *args, **kwargs):
        raise NotImplementedError("use 'dict['key'] = value' instead")
        
    def items(self):
        return self.__dict__.items()

class Base():

    def __init__(self,link=None):
        
        if link:
            self.initialized = True
        else:
            self.initialized = False

        
        self.webpage = None
        self.prased_webpage = None
        self.EMPTY = None
        self.link = link
        self.about = about_dict()
        self.chapter_list = {}
        '''{chapter_number:{chapter_name:chapter_link}}'''
        

        self.headers = {'User-Agent': 'RLMA (https://github.com/gala0sup/RLMA) Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    def _get_webpage(self):
        pass

    def _prase_webpage(self):
        pass

    def _set_info(self):
        logging.debug("settings up vars")
        pass

    def get_info(self,link):
        logging.info("getting info of (%s)",link)
        self.link = link
        self.initialized =True
        try:
            self._get_webpage()
            self._prase_webpage()
            self._set_info()

        except Exception as error:
            logging.error(error)
            logging.error("unable to retrive info of (%s)",self.link)
            raise

    def info(self,full=False):
        if not self.initialized:
            raise NotInitializedError()
        else:
            if full:
                return json.dumps({'link':self.link,**self.about,**self.chapter_list})
            else:
                return json.dumps({'link':self.link,**self.about})
