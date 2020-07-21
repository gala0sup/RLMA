'''Base class for light novel scrapers'''

from math import ceil
import json
import logging

from bs4 import BeautifulSoup
from kivy.network.urlrequest import UrlRequest

logger = logging.getLogger('RLMA')

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

class chapter_dict(object):
    '''{chapter_number:{chapter_name:chapter_link}}'''
    def __init__(self):
        self.__dict__ = {}
        
    def __setitem__(self,key,value):
        if type(value) == dict:
            if len(value) == 1:
                if key not in self.__dict__.keys():
                
                            if len(value[next(iter(value.keys()))])>0:
                                self.__dict__[key] = value
                            else:
                                raise ValueError('link cannot be empty')

                else:
                    
                    if len(value[next(iter(value.keys()))])>0:
                        for k in value.keys():
                            self.__dict__[key][k] = ''.join(value[k])
                    else:
                        raise ValueError('link cannot be empty')
            else:
                raise ValueError(('\ncannot assign multiple keys to a single key '+
                                    f'({{{key}:{value}}}'+
                                    f'\ncorrect format {{chapter_number:{{chapter_name:chapter_link}}}}'))
        else:
            raise ValueError(f"expected dict got {type(value).__name__} \n use dict['key'] = {{'key':'value'}}")
            
    def __getitem__(self,key):
        if key not in self.__dict__.keys():
            raise KeyError(f'{key} not defined')
        return self.__dict__[key]
    
    def keys(self):
        return self.__dict__.keys()
    
    def items(self):
        return self.__dict__.items()

class Base():

    def __init__(self,link=None,wait=False):
        
        if link:
            self.initialized = True
        else:
            self.initialized = False

        
        self.webpage = None
        self.prased_webpage = None
        self.EMPTY = None
        self.link = link
        self.about = about_dict()
        self.chapter_list = chapter_dict()
        '''{chapter_number:{chapter_name:chapter_link}}'''
        self.headers = {'User-Agent': 'RLMA (https://github.com/gala0sup/RLMA) Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        self._wait = wait
    def _get_webpage(self):
        logger.debug(f'{self._wait}')
        if not self.initialized:
            logger.error("class not Initialised")
            raise NotInitializedError("class not Initialised Try calling get_info('link')")
        else:
            try:
                logger.info("getting webpage (%s)",self.link)
                self.webpage = UrlRequest(self.link,on_success=self._parse_webpage,req_headers=self.headers)
                if self._wait:
                    self.webpage.wait()
            except Exception as error:
                logger.error(error)
                logger.warning("There was some Problem in getting the webpage (%s)",self.link)
            finally:
                if self._wait:
                    logger.debug("Status Code Returned by %s is %s",self.link,self.webpage.resp_status)

    def _parse_webpage(self,req,result):
        if not self.initialized:
            logger.error("class not Initialised")
            raise NotInitializedError("class not Initialised Try calling get_info('link')")
        else:
            try:
                logger.info("prasing webpage (%s)",self.link)
                self.prased_webpage = BeautifulSoup(result,'lxml')
                logger.debug("prased webpage")
            except Exception as error:
                logger.error(error)
                logger.error("unable to prase webpage")
                raise

    def _set_info(self):
        logger.debug("settings up vars")
        pass

    def get_info(self,link):
        logger.info("getting info of (%s)",link)
        self.link = link
        self.initialized =True
        try:
            self._get_webpage()
            self._set_info()

        except Exception as error:
            logger.error(error)
            logger.error("unable to retrive info of (%s)",self.link)
            raise

    def info(self,full=False):
        if not self.initialized:
            raise NotInitializedError()
        else:
            if full:
                return json.dumps({'link':self.link,**self.about,**self.chapter_list})
            else:
                return json.dumps({'link':self.link,**self.about})

    def chapters(self):
        if not self.initialized:
            raise NotInitializedError("Chapters() called before calling get_info('link')")
        else:
            return json.dumps({**self.chapter_list})
