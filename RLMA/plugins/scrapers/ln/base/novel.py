'''Base class for light novel scrapers'''

import json

class NotInitializedError(Exception):
    '''when info is called before get_info'''

    def __init__(self,message="info() is called before calling get_info('link')"):
        self.message = message
        super().__init__(self.message)


class Base():

    def __init__(self,link=None):
        self.initialized = False
        self.link = link
        self.webpage = None
        self.prased_webpage = None


        self.about = {
            'name':'',
            'chapters':'',
            'author':'',
            'status':'',
            'release':'',
            'updated':'',
            'discription':''
        }
        self.chapter_list = {}
        
    def _get_webpage(self):
        pass

    def _prase_webpage(self):
        pass

    def get_info(self,link):
        self._get_webpage()
        self._prase_webpage()
        self.initialized =True


    def info(self):
        if not self.initialized:
            raise NotInitializedError()
        else:
            return json.dumps({'link':self.link,**self.about,**self.chapter_list})
