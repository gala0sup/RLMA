'''Base class for light novel scrapers'''

import json
import logging

class NotInitializedError(Exception):
    '''when info is called before get_info'''

    def __init__(self,message="info() is called before calling get_info('link')"):
        self.message = message
        super().__init__(self.message)


class Base():

    def __init__(self,link=None):
        
        if link:
            self.initialized = True
        else:
            self.initialized = False

        
        self.webpage = None
        self.prased_webpage = None

        self.link = link
        self.about = {
            'CoverImage':'',
            'name':'',
            'chapters':'',
            'author':'',
            'status':'',
            'release':'',
            'updated':'',
            'discription':''

        }
        self.chapter_list = {}
        

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
        except:
            logging.error("unable to retrive info of (%s)",self.link)


    def info(self,full=False):
        if not self.initialized:
            raise NotInitializedError()
        else:
            if full:
                return json.dumps({'link':self.link,**self.about,**self.chapter_list})
            else:
                return json.dumps({'link':self.link,**self.about})
