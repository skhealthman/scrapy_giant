# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import pytz
from datetime import datetime

from scrapy import log
from crawler.pipelines.base_pipeline import BasePipeline
from handler.hisdb_handler import *

__all__ = ['TwseHisCreditPipeline']

class TwseHisCreditPipeline(BasePipeline):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def __init__(self, crawler):
        super(TwseHisCreditPipeline, self).__init__()
        self._name = 'twsehiscredit'
        kwargs = {
            'debug': crawler.settings.getbool('GIANT_DEBUG'),
            'opt': 'twse'
        }
        self._db = TwseHisDBHandler(**kwargs)

    def process_item(self, item, spider):
        if spider.name not in [self._name]:
            return item
        item = self._clear_item(item)
        item = self._update_item(item)
        self._write_item(item)

    def _clear_item(self, item):
        jstream = self._encode_item(item)
        return self._decode_item(jstream)

    def _update_item(self, item):
        # finance 單位: 交易單位
        # bearish 單位: 股
        frame = pd.DataFrame.from_dict(item['data']).dropna()
        if frame.empty:
            return
        def _encode_datetime(it):
            yy, mm, dd = map(int, it.split('-'))
            return datetime(yy, mm, dd, 0, 0, 0, 0, pytz.utc)
        frame['date'] = [_encode_datetime(it) for it in frame['date']]
        frame['stockid'] = frame['stockid']
        frame['stocknm'] = frame['stocknm']
        frame['preremain'] = frame['preremain'].astype(int)  
        frame['buyvolume'] = frame['buyvolume'].astype(int) 
        frame['sellvolume'] = frame['sellvolume'].astype(int) 
        frame['daytrade'] = frame['daytrade'].astype(int) 
        frame['curremain'] = frame['curremain'].astype(int) 
        frame['limit'] = frame['limit'].astype(long) 
        item = frame.T.to_dict().values()
        log.msg("item: %s" % (item), level=log.DEBUG)
        return item

    def _write_item(self, item):
        self._db.credit.insert_raw(item)
