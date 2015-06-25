# -*- coding: utf-8 -*-

from crawler.spider.twsehisfuture_spider import TwseHisFutureSpider
from handler.hisdb_handler import *

__all__ = ['OtcHisFutureSpider']

class OtcHisFutureSpider(TwseHisFutureSpider):
    name = 'otchisfuture'

    def __init__(self, crawler):
        super(OtcHisFutureSpider, self).__init__()
        kwargs = {
            'debug': crawler.settings.getbool('GIANT_DEBUG'),
            'limit': crawler.settings.getint('GIANT_LIMIT'),
            'opt': 'otc'
        }
        self._id = OtcIdDBHandler(**kwargs)
        self._table = {}