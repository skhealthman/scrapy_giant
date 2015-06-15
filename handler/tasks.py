# -*- coding: utf-8 -*-

import pandas as pd
import json
from bson import json_util
from handler.iddb_handler import TwseIdDBHandler, OtcIdDBHandler
from handler.hisdb_handler import TwseHisDBHandler, OtcHisDBHandler

from celery.utils.log import get_task_logger
logger = get_task_logger('handler')

hisdb_tasks = {
    'twse': TwseHisDBHandler,
    'otc': OtcHisDBHandler
}

iddb_tasks = {
    'twse': TwseIdDBHandler,
    'otc': OtcIdDBHandler
}

def collect_hisitem(collect):
    """ as middleware cascade collect raw hisstock/histoptrader/hiscredit to item
    filer priority 0>1>2
    """

    item = {}
    opt = collect['opt']
    assert(opt in ['twse', 'otc'])
    frame = collect['frame']
    cols = frame.keys()
    assert(cols <= ['hisstock', 'histrader', 'hiscredit', 'hisfuture'])
    assert(len(set([frame[col]['base'] for col in cols if frame[col]['on']]))==1)

    idhandler = iddb_tasks[opt](debug=collect['debug'])
    dbhandler = hisdb_tasks[opt](**collect)

    stockids = [i for i in idhandler.stock.get_ids()] if collect['method'] == 'list' else []
    [stockids.extend(frame[col]['stockids']) for col in cols if frame[col]['on']]
    stockids = list(set(stockids))

    traderids =[i for i in idhandler.trader.get_ids()] if collect['method'] == 'list' else []
    [traderids.extend(frame[col]['traderids']) for col in ['histrader'] if frame[col]['on'] and frame[col]['traderids']]
    traderids = list(set(traderids))

    pstockids = []

    for p in set([v['priority'] for v in frame.values()]):
        pool = filter(lambda x: x[1]['priority'] == p, frame.items())
        for i, it in enumerate(pool):
            print frame[it[0]]
            if i == len(pool)-1:
                frame[it[0]].update({'do':'join'})
            else:
                frame[it[0]].update({'do':'parallel'})
             
    for it, p in sorted(frame.items(), key=lambda x: x[1]['priority']):
        do = frame[it]['do']

        if it == 'hisstock':
            if frame[it]['on']:
                [frame[it].pop(k) for k in ['on', 'priority', 'do']]
                frame[it]['stockids'] = stockids
                dt = dbhandler.stock.query_raw(**frame[it])
                if dt:
                    item.update({'stockitem': dt})
                    pstockids.extend([i['stockid'] for i in dt])
                    if do == 'join':
                        stockids = pstockids
                        pstockids = []
                frame[it].update({
                    'on': True,
                    'priority': 0
                    })

        if it == 'hiscredit':
            if frame[it]['on']:
                [frame[it].pop(k) for k in ['on', 'priority', 'do']]
                frame[it]['stockids'] = stockids
                dt = dbhandler.credit.query_raw(**frame[it])
                if dt:
                    item.update({'credititem': dt})
                    pstockids.extend([i['stockid'] for i in dt])
                    if do == 'join':
                        stockids = pstockids
                        pstockids = []
                frame[it].update({
                    'on': True,
                    'priority': 0
                    })

        if it == 'histrader':
            if frame[it]['on']:
                [frame[it].pop(k) for k in ['on', 'priority', 'do']]
                frame[it]['stockids'] = stockids
                frame[it]['traderids'] = traderids
                dt = dbhandler.trader.query_raw(**frame[it])
                if dt:
                    item.update({'traderitem': dt})
                    pstockids.extend([i['stockid'] for i in dt])
                    if do == 'join':
                        stockids = pstockids
                        pstockids = []
                    traderids = [i['traderid'] for i in dt]
                frame[it].update({
                    'on': True,
                    'priority': 0
                    })

        if it == 'hisfuture':
            if frame[it]['on']:
                [frame[it].pop(k) for k in ['on', 'priority', 'do']]
                frame[it]['stockids'] = stockids
                dt = dbhandler.future.query_raw(**frame[it])
                if dt:
                    item.update({'futureitem': dt})
                    pstockids.extend([i['stockid'] for i in dt])
                    if do == 'join':
                        stockids = pstockids
                        pstockids = []
                frame[it].update({
                    'on': True,
                    'priority': 0
                    })  

    collect['status'] = 'run' if collect['status'] == 'start' else 'finish'

    if 'debug' in collect and collect['debug']:
        print json.dumps(dict(collect), sort_keys=True, indent=4, default=json_util.default, ensure_ascii=False)
    
    if collect['status'] == 'finish':
        return item, dbhandler
    else:
        return collect_hisitem(collect)  


def collect_hisframe(collect):
    """  as middleware collect raw hisstock/histoptrader/hiscredit to df
    <stockid>                                | <stockid> ...
                open| high| financeused| top0|           open | ...
    20140928    100 | 101 | 0,2        | 100 |20140928 | 110  | ...
    20140929    100 | 102 | 0.3        | 200 |20140929 | 110  | ...
    """

    if 'debug' in collect and collect['debug']:
        print json.dumps(dict(collect), sort_keys=True, indent=4, default=json_util.default, ensure_ascii=False)

    group = []
    opt = collect['opt']
    assert(opt in ['twse', 'otc'])
    frame = collect['frame']
    cols = frame.keys()
    assert(cols <= ['hisstock', 'histrader', 'hiscredit', 'hisfuture'])
    assert(len(set([frame[col]['base'] for col in cols if frame[col]['on']]))==1)

    dbhandler = hisdb_tasks[opt](**collect)
    for it in frame:
        if it == 'hisstock':
            if frame[it]['on']:
                frame[it].pop('on')
                dbhandler.stock.ids = frame[it]['stockids']
                frame[it].update({'callback': dbhandler.stock.to_pandas})
                frame[it].pop('priority')
                df = dbhandler.stock.query_raw(**frame[it])
                if not df.empty:
                    group.append(df)
        if it == 'histrader':
            if frame[it]['on']:
                frame[it].pop('on')
                dbhandler.trader.ids = frame[it]['stockids']
                frame[it].update({'callback': dbhandler.trader.to_pandas})
                frame[it].pop('priority')
                df = dbhandler.trader.query_raw(**frame[it])
                if not df.empty:
                    group.append(df)
        if it == 'hiscredit':
            if frame[it]['on']:
                frame[it].pop('on')
                dbhandler.credit.ids = frame[it]['stockids']
                frame[it].update({'callback': dbhandler.credit.to_pandas})
                frame[it].pop('priority')
                df = dbhandler.credit.query_raw(**frame[it])
                if not df.empty:
                    group.append(df)
        if it == 'hisfuture':
            if frame[it]['on']:
                frame[it].pop('on')
                dbhandler.future.ids = frame[it]['stockids']
                frame[it].update({'callback': dbhandler.future.to_pandas})
                frame[it].pop('priority')
                df = dbhandler.future.query_raw(**frame[it])
                if not df.empty:
                    group.append(df)
    if group:
        panel = pd.concat(group, axis=2).fillna(0)
        return panel, dbhandler
    return pd.Panel(), dbhandler

def collect_relitem(collect):
    pass

def collect_relframe(collect):
    pass
