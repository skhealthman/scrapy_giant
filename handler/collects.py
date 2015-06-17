# -*- coding: utf-8 -*-

def create_hiscollect(**kwargs):
    """ as context event """
    starttime = kwargs.pop('starttime', None)
    endtime = kwargs.pop('endtime', None)
    stockids =  kwargs.pop('stockids', [])
    traderids = kwargs.pop('traderids', [])
    opt = kwargs.pop('opt', None)
    algorithm = kwargs.pop('algorithm', None)
    debug = kwargs.pop('debug', False)
    method = kwargs.pop('method', None)

    collect = {
        'starttime': starttime,
        'endtime': endtime,
        'stockids': stockids,
        'traderids': traderids,
        'algorithm': algorithm,
        'opt': opt,
        'method': method,
        'debug': debug,
        'status': 'start', 
        'frame': {
            'hisstock': {
                'on': False,
                'starttime': starttime,
                'endtime': endtime,
                'stockids': stockids,
                'base': 'stock',
                'order': ['-totalvolume', '-totaldiff'],
                'callback': None,
                'limit': 10,
                'priority': 0
            },
            'hiscredit': {
                'on': False,
                'starttime': starttime,
                'endtime': endtime,
                'stockids': stockids,
                'base': 'stock',
                'order': ['-financeused', '-bearishused'],
                'callback': None,
                'limit': 10,
                'priority': 1
            },
            'hisfuture': {
                'on': False,
                'starttime': starttime,
                'endtime': endtime,
                'stockids': stockids,
                'base': 'stock',
                'order': ['-totaldiff'],
                'callback': None,
                'limit': 10,
                'priority': 2
            },
            'histrader': {
                'on': False,
                'starttime': starttime,
                'endtime': endtime,
                'stockids': stockids,
                'traderids': traderids,
                'base': 'stock',
                'order': ['-totalvolume'],
                'callback': None,
                'limit': 10,
                'priority': 3,
            }
        }
    }
    return collect

def create_relcollect(**kwargs):
    collect = {}
    return collect