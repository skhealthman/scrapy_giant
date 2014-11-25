# -*- coding: utf-8 -*-

import pandas as pd
import pytz
from collections import OrderedDict
from bson import json_util

from mongoengine import *
from bin.start import switch
from bin.mongodb_driver import MongoDBDriver
from handler.models import (
    TwseHisColl, OtcHisColl, StockData, TraderData,
    TraderInfo, TraderMapColl, TraderMapData, StockMapColl, StockMapData
)

# use mongoengine(high level mongodb drive) as ORM data backend for Django access

__all__ = ['TwseHisDBHandler', 'OtcHisDBHandler']


class TwseHisDBHandler(object):

    def __init__(self):
        host, port = MongoDBDriver._host, MongoDBDriver._port
        connect('twsehisdb', host=host, port=port, alias='twsehisdb')
        twsehiscoll = switch(TwseHisColl, 'twsehisdb')
        self._stock = StockHisDBHandler(twsehiscoll)
        self._trader = TraderHisDBHandler(twsehiscoll)

    @property
    def stock(self):
        return self._stock

    @property
    def trader(self):
        return self._trader

    def transform_all_data(self, starttime, endtime, stockids=[], traderids=[], order='totalvolume', limit=10):
        """ transfrom stock/trader data as pandas panel """
        stockdt = self._stock.query(starttime, endtime, stockids)
        stockdt = self._stock.to_pandas(stockdt)
        traderdt = self._trader.query(starttime, endtime, stockids, traderids, 'stock', order, limit)
        traderdt = self._trader.to_pandas(traderdt)
        return pd.concat([stockdt, traderdt], axis=2).fillna(0)


class OtcHisDBHandler(TwseHisDBHandler):

    def __init__(self):
        super(OtcHisDBHandler, self).__init__()
        host, port = MongoDBDriver._host, MongoDBDriver._port
        connect('otchisdb', host=host, port=port, alias='otchisdb')
        otchiscoll = switch(OtcHisColl, 'otchisdb')
        self._stock = StockHisDBHandler(otchiscoll)
        self._trader = TraderHisDBHandler(otchiscoll)


class StockHisDBHandler(object):

    def __init__(self, coll):
        """ specified hiscoll as twse/otc """
        host, port = MongoDBDriver._host, MongoDBDriver._port
        connect('stockhisdb', host=host, port=port, alias='stockhisdb')
        self._mapcoll = switch(StockMapColl, 'stockhisdb')
        self._mapcoll.drop_collection()
        self._coll = coll
        self._ids = []

    @property
    def ids(self):
        return self._ids

    @ids.setter
    def ids(self, ids):
        self._ids = ids

    def drop(self):
        self._mapcoll.drop_collection()
        self._ids = []

    def insert(self, item):
        """ insert stock item to db """
        for it in item:
            data = {
                'open': it['open'],
                'high': it['high'],
                'low': it['low'],
                'close': it['close'],
                'volume': it['volume']
            }
            data = StockData(**data)
            cursor = self._coll.objects(Q(date=it['date']) & Q(stockid=it['stockid']))
            cursor = list(cursor)
            if len(cursor) == 0:
                coll = self._coll().save()
            else:
                coll = cursor[0]
            coll.stockid = it['stockid']
            coll.date = it['date']
            coll.data = data
            coll.save()

    def query(self, starttime, endtime, stockids=[]):
        """ return orm
        <stockid>                               | <stockid> ...
                    open| high| low|close|volume|          | open | ...
        20140928    100 | 101 | 99 | 100 | 100  | 20140928 | 11   | ...
        20140929    100 | 102 | 98 | 99  | 99   | 20140929 | 11   | ...
        """
        cursor = self._coll.objects(Q(date__gte=starttime) & Q(date__lte=endtime) & Q(stockid__in=stockids))
        map_f = """
            function () {
                var key =  { stockid : this.stockid };
                var value = {
                    data: [{
                        date: this.date,
                        open: this.data.open,
                        high: this.data.high,
                        low: this.data.low,
                        close: this.data.close,
                        price: this.data.close,
                        volume: this.data.volume
                     }]
                };
                emit(key, value);
            }
        """
        reduce_f = """
          function (key, values) {
                var redval = {
                    data: []
                };
                if (values.length == 0) {
                    return redval;
                }
                for (var i=0; i < values.length; i++) {
                    redval.data = values[i].data.concat(redval.data);
                }
                return redval;
            }
        """
        ids = stockids
        mkey = 'stockid'
        results = cursor.map_reduce(
            map_f,
            reduce_f,
            'stockmap')
        results = list(results)
        for id in ids:
            pool = list(filter(lambda x: x.key[mkey]==id, results))
            for it in pool:
                coll = self._mapcoll().save()
                for data in it.value['data']:
                    coll.datalist.append(
                        StockMapData(
                            date=data['date'],
                            open=data['open'],
                            high=data['high'],
                            low=data['low'],
                            close=data['close'],
                            price=data['price'],
                            volume=data['volume']))
                coll.stockid = it.key['stockid']
                coll.save()
        return self._mapcoll.objects

    def to_pandas(self, cursor):
        """ transform orm to pandas panel
        """
        item = OrderedDict()
        for it in cursor:
            index, data = [], []
            for ii in it.datalist:
                index.append(pytz.timezone('UTC').localize(ii.date))
                data.append({
                    'open': ii.open,
                    'high': ii.high,
                    'low': ii.low,
                    'close': ii.close,
                    'price': ii.price,
                    'volume': ii.volume
                })
            if index and data:
                id = it.stockid
                item.update({
                    id: pd.DataFrame(data, index=index).fillna(0)
                 })
        return pd.Panel(item)

    def to_json(self, cursor):
        """ transform orm to json stream
        """
        return cursor.to_json(sort_keys=True, indent=4, default=json_util.default, ensure_ascii=False)


class TraderHisDBHandler(object):

    def __init__(self, coll):
        """ specified hiscoll as twse/otc """
        host, port = MongoDBDriver._host, MongoDBDriver._port
        connect('traderhisdb', host=host, port=port, alias='traderhisdb')
        self._mapcoll = switch(TraderMapColl, 'traderhisdb')
        self._mapcoll.drop_collection()
        self._coll = coll
        self._ids = []

    @property
    def ids(self):
        return self._ids

    @ids.setter
    def ids(self, ids):
        self._ids = ids

    def drop(self):
        self._mapcoll.drop_collection()
        self._ids = []

    def insert(self, item):
        """ insert trader item to db """
        toplist = []
        for it in item['toplist']:
            data = {
                'avgbuyprice': it['data']['avgbuyprice'],
                'buyvolume': it['data']['buyvolume'],
                'avgsellprice': it['data']['avgsellprice'],
                'sellvolume': it['data']['sellvolume'],
                'totalvolume': it['data']['totalvolume']
            }
            toplist.append(
                TraderInfo(
                    traderid=it['traderid'],
                    tradernm=it['tradernm'],
                    data=TraderData(**data)))
        cursor = self._coll.objects(Q(date=item['date']) & Q(stockid=item['stockid']))
        cursor = list(cursor)
        if len(cursor) == 0:
            coll = self._coll().save()
        else:
            coll = cursor[0]
        coll.stockid = item['stockid']
        coll.date = item['date']
        coll.toplist = toplist
        coll.save()

    def query(self, starttime, endtime, stockids=[], traderids=[],
            base='stock', order='totalvolume', limit=10):
        """ get rank toplist volume stock/trader data
            <stockid>                                               <stockid>
                     | top0_v/p_<traderid> | top1 | ... top10 |          | top0_<traderid>
            20140928 |  100               |   30    |              | 20140928 | ...
            20140929 |    0               |   20    |              | 20140929 | ...
            -------------------------------------------------------------------------
                        100                   50

            <traderid>                                              <traderid>
                     | top0_<stockid> | top1  | ... top10 |          | top0_<traderid>
            20140928 |  100               |   30    |              | 20140928 | ...
            20140929 |    0               |   20    |              | 20140929 | ...
            -------------------------------------------------------------------------
                        100                   50
        """
        map_f = """
            function () {
                for (var i=0; i < this.toplist.length; i++) {
                    var key =  { traderid: this.toplist[i].traderid, stockid: this.stockid };
                    var totalvolume = this.toplist[i].data.totalvolume;
                    var volume = this.toplist[i].data.buyvolume - this.toplist[i].data.sellvolume;
                    var price = 0;
                    var hit = 0;
                    var ratio = 0;
                    if (volume > 0) {
                        price = this.toplist[i].data.avgbuyprice;
                    } else if (volume <0) {
                        price = this.toplist[i].data.avgsellprice;
                    } else {
                        price = 0;
                    }
                    if (totalvolume >0) {
                        hit = 1;
                        ratio = totalvolume / this.data.volume * 100;
                    } else {
                        hit = 0;
                        ratio = 0;
                    }
                    var value = {
                        totalvolume: totalvolume,
                        hit: hit,
                        data: [{ date: this.date, ratio: ratio, price: price, volume: volume }]
                    };
                    emit(key, value);
                }
            }
        """
        reduce_f = """
            function (key, values) {
                var redval = {
                    totalvolume: 0,
                    hit: 0,
                    data: []
                };
                if (values.length == 0) {
                    return redval;
                }
                for (var i=0; i < values.length; i++) {
                    redval.totalvolume += values[i].totalvolume;
                    redval.hit += values[i].hit;
                    redval.data = values[i].data.concat(redval.data);
                }
                return redval;
            }
        """
        ids = stockids if base == 'stock' else traderids
        mkey = 'stockid' if base == 'stock' else 'traderid'
        vkey = 'traderid' if base == 'stock' else 'stockid'
        assert(order in ['totalvolume', 'hit', 'ratio'])
        cursor = self._coll.objects(
            Q(date__gte=starttime) & Q(date__lte=endtime) &
            (Q(stockid__in=stockids) | Q(toplist__traderid__in=traderids)))
        results = cursor.map_reduce(
            map_f,
            reduce_f,
            'toptradermap')
        results = list(results)
        for id in ids:
            pool = list(filter(lambda x: x.key[mkey]==id, results))
            pool = sorted(pool, lambda x: x.value[order], reverse=True)[:limit]
            for i, it in enumerate(pool):
                coll = self._mapcoll().save()
                for data in it.value['data']:
                    coll.datalist.append(
                        TraderMapData(
                            ratio=data['ratio'],
                            price=data['price'],
                            volume=data['volume'],
                            date=data['date']))
                coll.traderid = it.key['traderid']
                coll.stockid = it.key['stockid']
                coll.alias = "top%d" % (i)
                coll.base = base
                coll.save()
        return self._mapcoll.objects

    def to_pandas(self, cursor):
        """ transform orm to pandas panel
        """
        bases = list(set([it.base for it in cursor]))
        assert(len(bases)<2)
        item = OrderedDict()
        for it in cursor:
            index, data = [], []
            for ii in it.datalist:
                index.append(pytz.timezone('UTC').localize(ii.date))
                data.append({
                    "%s_ratio" % (it.alias): ii.ratio,
                    "%s_price" % (it.alias): ii.price,
                    "%s_volume" % (it.alias): ii.volume
                })
            if index and data:
                id = it.stockid if bases[0] == 'stock' else it.traderid
                item.update({
                    id: pd.DataFrame(data, index=index).fillna(0)
                 })
        return pd.Panel(item)

    def to_json(self, cursor):
        """ transform orm to json
        """
        return cursor.to_json(sort_keys=True, indent=4, default=json_util.default, ensure_ascii=False)

    def map_alias(self, ids=[], base='stock', aliases=['top0'], cursor=None):
        """ get alias map
        """
        mapcoll = cursor if cursor else self._mapcoll
        if base == 'stock':
            cursor = mapcoll.objects(Q(base=base) & Q(stockid__in=ids) & Q(alias__in=aliases))
            cursor = list(cursor)
            return [it.traderid for it in cursor]
        else:
            cursor = mapcoll.objects(Q(base=base) & Q(traderid__in=ids) & Q(alias__in==aliases))
            cursor = list(cursor)
            return [it.stockid for it in cursor]