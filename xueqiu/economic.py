# -*- coding: utf-8 -*-

"""
xueqiu.economic
~~~~~~~~~~~~~~~

This module implements an economic data api.

:copyright: (c) 2019 by 1dot75cm.
:license: MIT, see LICENSE for more details.
"""

__all__ = ['get_economic', 'get_economic_of_china']

from .utils import sess
from . import api
import pandas as pd
import arrow
import json


def get_economic(name: str = 'help', search: str = '中国'):
    """Get economic data from investing.com."""
    form_data = {'search_text':search,'tab':'ec_event','offset':0,'limit':270}
    resp = sess.post(api.economic_search, data=form_data)
    events = {i['name']:i['dataID'] for i in resp.json()['ec_event']}
    if name == 'help': return events
    elif name in events.keys() or isinstance(int(name), int):
        resp = sess.get(api.economic % (events.get(name) or name))
        cols = ['timestamp','actual','actual_state','forecast','revised']
        df = pd.DataFrame(resp.json()['attr'])[cols]
        df['date'] = df['timestamp'].apply(lambda x:arrow.get(x/1000).datetime)
        return df.set_index('date').drop('timestamp',axis=1)


def get_economic_of_china(indicator: str = 'help',
                          region: str = '',
                          category: str = 'year',
                          search: str = '',
                          time_period: str = ''):
    """Get economic data of china from data.stats.gov.cn.

    :param indicator: (optional) economic indicators, default is `help`.
    :param region: (optional) region, used to `state` and `city` categories only.
    :param category: (optional) category of economic indicators, default is `year`.
        value: month quarter year month_by_state quarter_by_state
            year_by_state month_by_city year_by_city
    :param search: (optional) search indicators, default is `''`.
    :param time_period: (optional) period of time, default is `''`.
        value: month: 201810,201812 201801-201809
               quarter: 2018A,2018B,2018C,2018D
               year: 2017,2018 2016-2018
               other: 2014-,last5
    :return: the economic data of china.
    :rtype: `pd.DataFrame`.
    """
    process_month = lambda x:x[:4]+'-'+x[4:]
    process_quarter = lambda x:x[:-1]+dict(A='Q1',B='Q2',C='Q3',D='Q4')[x[-1]]
    cg = {'month': ['A01','hgyd',process_month],
          'quarter': ['B01','hgjd',process_quarter],
          'year': ['C01','hgnd',lambda x:x],
          'month_by_state': ['E0101','fsyd',process_month],
          'quarter_by_state': ['E0102','fsjd',process_quarter],
          'year_by_state': ['E0103','fsnd',lambda x:x],
          'month_by_city': ['E0104','csyd',process_month],
          'year_by_city': ['E0105','csnd',process_quarter]}
    # search indicators
    def _search(s):
        if s == 'region':
            tree = cg[category][1] == 'csnd' and '000000' or '00'
            data = dict(m='findZbXl',db=cg[category][1],wd='reg',treeId=tree)
        else:
            data = dict(m='findGjcx',db=cg[category][1],wd='zb',s=s)
        resp = sess.post(api.china_stats_adv, data=data)
        return [{'id':i['id'],'name':i['name']} for i in resp.json()]
    if search: return _search(search)
    if indicator == 'help': return 'please add search param.'
    # get data
    inds, regs = indicator.split(','), region.split(',')  # list
    query = [{"wd":"zb","zb":inds}]
    category in list(cg.keys())[-5:] and query.append({"wd":"reg","zb":regs})  # region
    data = {'c': json.dumps(query)}
    params = {'m':'advquery','cn':cg[category][0]}
    sess.post(api.china_stats_adv, params=params, data=data)
    ## region options ##
    _reg = {'wds':[], 'row':'zb', 'idx':0}  # region 默认
    if category in list(cg.keys())[-5:] and len(regs)>=2:  # region 多个地区，一个指标
        _reg = {'wds':[{"wdcode":"zb","valuecode":inds[0]}], 'row':'reg', 'idx':1}
    elif category in list(cg.keys())[-5:] and len(regs)<2:  # region 多个指标，一个地区
        _reg = {'wds':[{"wdcode":"reg","valuecode":regs[0]}], 'row':'zb', 'idx':0}
    ## end region options ##
    params = dict(m='QueryData',dbcode=cg[category][1],rowcode=_reg['row'],colcode='sj',
        wds=json.dumps(_reg['wds']), dfwds=json.dumps([{"wdcode":"sj","valuecode":time_period}]))
    resp = sess.get(api.china_stats, params=params).json()['returndata']
    # dataframe
    index = [cg[category][2](i['code']) for i in resp['wdnodes'][-1]['nodes']]  # 时间
    ck = {i['code']:i['name'] for i in resp['wdnodes'][_reg['idx']]['nodes']}
    data = {i:[] for i in ck.values()}
    for i in resp['datanodes']:
        data[ck[i['wds'][_reg['idx']]['valuecode']]].append(i['data']['data'])
    return pd.DataFrame(data, index=pd.to_datetime(index))