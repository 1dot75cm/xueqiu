# -*- coding: utf-8 -*-

"""
xueqiu.stock
~~~~~~~~~~~~

This module implements some stock methods.

:copyright: (c) 2019 by 1dot75cm.
:license: MIT, see LICENSE for more details.
"""

__all__ = ['get_data_yahoo', 'get_data_invest', 'get_quote_yahoo', 'get_stock_margin',
           'get_hsgt_history', 'get_hsgt_top10', 'get_hsgt_holding']

from .utils import check_symbol
from .utils import sess
from .utils import str2date
from .utils import search_invest
from .sheet import spindices
from . import api
from lxml import html
from io import StringIO, BytesIO
import pandas_datareader.data as web
import pandas_market_calendars as mcal
import pandas as pd
import arrow
import gzip
import re


def get_data_yahoo(symbol: str, start: str = '-1y', end: str = None,
                   session = sess, **kwargs):
    """a yahoo stock api wrapper.

    :param symbol: stock symbol or code.
    :param start: (optional) start date of the custom return, default is `-1y`.
        value: -nd -nw -nm -ny cyear or YYYY-MM-DD
    :param end: (optional) the end date of the results, default is `now`.
    :param session: (optional) use an existing session, default is `sess`.
    :param **kwargs: please see `pandas_datareader.data.DataReader` reference.
    :return: pd.DataFrame
    """
    begin = str2date(start).format('YYYY-MM-DD')
    df = web.get_data_yahoo(check_symbol(symbol,'yahoo'), start=begin,
            end=end, session=session, **kwargs)
    return df


def get_quote_yahoo(symbol: str, session = sess, **kwargs):
    """get stock summary from yahoo.com."""
    symbol = check_symbol(symbol,'yahoo')
    return web.get_quote_yahoo(symbol, session=session, **kwargs)


def get_data_invest(symbol: str = '', start: str = '-1y', end: str = arrow.now(),
                    period: str = 'day', query: str = ''):
    """get stock data from investing.com."""
    header = {'Origin':api.invest, 'Referer':api.invest}
    begin = str2date(start).format('YYYY/MM/DD')
    end = arrow.get(end).format('YYYY/MM/DD')
    intl = {'day':'Daily', 'week':'Weekly', 'month':'Monthly'}
    if query: return search_invest(query)
    elif symbol:
        form_data = {'action':'historical_data', 'curr_id':symbol,
            'st_date':begin, 'end_date':end, 'interval_sec':intl[period]}
        resp = sess.post(api.invest_history, data=form_data, headers=header)
        tree = html.fromstring(resp.text)
        cols = tree.xpath(api.x_invest_history[0])[:-1]
        data = [i.xpath(api.x_invest_history[2]) for i in tree.xpath(api.x_invest_history[1])]
        data = [map(lambda x:x.replace(',',''), i) for i in data]
        df = pd.DataFrame(data, columns=cols, dtype=float).set_index('date').sort_index()
        df.index = pd.to_datetime(df.index, unit='s')
        return df.rename(columns={'price':'close'})


def get_data_netease(symbol: str, start: str = '-1y', end: str = arrow.now()):
    """get stock data from 163.com."""
    fields = 'TOPEN;HIGH;LOW;TCLOSE;VOTURNOVER;VATURNOVER'
    cols = 'date,code,name,open,high,low,close,volume,amount'
    begin = str2date(start).format('YYYYMMDD')
    end = arrow.get(end).format('YYYYMMDD')
    params = dict(code=check_symbol(symbol,'163'),
                  start=begin, end=end, fields=fields)
    resp = sess.get(api.stock_history_ntes, params=params)
    df = pd.read_csv(StringIO(resp.text), header=0, names=cols.split(','),
                     index_col='date', parse_dates=True)
    return df.sort_index()


def get_data_spindices(symbol: str):
    """get index data from spindices.com."""
    cols = {4: 'date,total_return,net_total_return,price',
            3: 'date,total_return,price',
            2: 'date,price'}
    params = {'hostIdentifier': '113d3fd3-ecaf-400f-9058-bbce16ec2390',
              'selectedModule': 'PerformanceGraphView',
              'selectedSubModule': 'Graph',
              'yearFlag': 'tenYearFlag',
              'indexId': spindices.get(symbol.lower())}
    resp = sess.get(api.spindices_history, params=params)
    df = pd.read_excel(BytesIO(resp.content), parse_dates=True,
                       skiprows=6, skipfooter=4)
    df.columns = cols[df.columns.size].split(',')
    return df.set_index('date')


def get_data_csindex(symbol: str, total_return: bool = False):
    """get index data from csindex.com.cn."""
    header = {'Origin':'', 'Referer':''}
    col1 = 'date,code,fullcnname,cnname,fullname,name,open,high,low,close,'\
           'change,percent,volume,amount,numofcons,pe1,pe2,div1,div2'
    col2 = 'date,code,fullcnname,cnname,fullname,name,close,change,percent'
    if total_return:
        resp = sess.get(api.csindex_perf%symbol, headers=header)
        df1 = pd.read_excel(BytesIO(resp.content), 0, names=col1.split(','), index_col='date', parse_dates=True)
        df2 = pd.read_excel(BytesIO(resp.content), 1, names=col2.split(','), index_col='date', parse_dates=True)
        df3 = pd.DataFrame({k:v.close.tolist() for k,v in df2.groupby('code')}, index=df1.index)
        df = df1.merge(df3, left_index=True, right_index=True).sort_index()
    else:
        resp = sess.get(api.csindex_history%symbol, headers=header)
        df = pd.DataFrame(resp.json())[['tradedate','tclose']]
        df.columns = ['date','close']
        df = df.set_index('date')
        df.index = pd.to_datetime(df.index)
    return df


def get_data_sseindex(symbol: str):
    """get index data from sse.com.cn."""
    header = {'Origin':'', 'Referer':'http://www.sse.com.cn/market/sseindex/quotation/'}
    params = {'indexCode':symbol, 'codeType':'t'}
    resp = sess.get(api.sseindex_perf, headers=header, params=params)
    df = pd.read_excel(BytesIO(resp.content), names=['date','total_return'],
                       index_col='date', parse_dates=True)
    return df.sort_index()


def get_stock_margin(code: str = '', begin: str = '-3m', page: int = 1, mkt_type: str = 'all'):
    """get stock margin. 融资融券"""
    begin = str2date(begin)
    count = (arrow.now()-begin).days
    mkt = {'sh':['HS',"(market='SH')"], 'sz':['HS',"(market='SZ')"], 'all':['LS','']}
    params = dict(token='70f12f2f4f091e459a279469fe49eca5', st='tdate', sr=-1, p=page, ps=count) #js={pages:(tp),data:(x)}
    stock_param = dict(type='RZRQ_DETAIL_NJ', filter='(scode=%s)'%check_symbol(code)[2:])
    mkt_param = dict(type='RZRQ_%sTOTAL_NJ'%mkt[mkt_type][0], filter=mkt[mkt_type][1], mk_time=1)
    params.update(code and stock_param or mkt_param)
    resp = sess.get(api.margin, params=params)
    df = pd.read_json(resp.text).set_index('tdate')
    df.index = pd.to_datetime(df.index)
    return df.rename(columns=sheet.margin)


def get_hsgt_history(mkt_type: str = 'shgt', begin: str = '-1m', page: int = 1):
    """get shanghai-shenzhen-hongkong stock history. 沪深港通历史数据"""
    begin = str2date(begin)
    count = (arrow.now()-begin).days
    mkt = {'shgt':1, 'szgt':3, 'hksh':2, 'hksz':4}
    params = dict(token='70f12f2f4f091e459a279469fe49eca5', type='HSGTHIS',
        st='DetailDate', sr=-1, p=page, ps=count, filter='(MarketType=%s)'%mkt[mkt_type])
    resp = sess.get(api.margin, params=params)
    df = pd.read_json(resp.text).set_index('DetailDate')
    df.index = pd.to_datetime(df.index)
    return df.rename(columns=sheet.hsgt)


def get_hsgt_top10(mkt_type: str = 'shgt', date: str = arrow.now()):
    """get shanghai-shenzhen-hongkong top10 stock. 沪深港通top10"""
    _date = arrow.get(date).format('YYYY-MM-DD')
    mkt = {'shgt':[1,'hgt'], 'szgt':[3,'sgt'], 'hksh':[2,'ggt'], 'hksz':[4,'ggt']}
    params = dict(token='70f12f2f4f091e459a279469fe49eca5', type='HSGTCJB',
        sty=mkt[mkt_type][1], st='', sr=-1, page=1, pagesize=50,
        filter='(MarketType=%s)(DetailDate=^%s^)'%(mkt[mkt_type][0], _date))
    resp = sess.get(api.margin, params=params)
    df = pd.read_json(resp.text).drop(columns=['MarketType','DetailDate'])
    if mkt_type == 'hksh':
        df = df.drop(columns=['GGTSCJJE','GGTSJME','GGTSMCJE','GGTSMRJE','Rank1'])
    elif mkt_type == 'hksz':
        df = df.drop(columns=['GGTHCJJE','GGTHJME','GGTHMCJE','GGTHMRJE','Rank'])
        df = df.rename({'Rank1':'Rank'}, axis=1)
    else:
        df = df.drop(columns='Rank1')
    return df.set_index('Rank').sort_index()


def get_hsgt_holding(code: str = '', mkt_type: str = 'north', date: str = arrow.now(),
                     page: int = 1, count: int = 50):
    """get shanghai-shenzhen-hongkong stock holding. 沪深港通持股"""
    #沪港通及深港通持股纪录查询服务
    #http://sc.hkexnews.hk/TuniS/www2.hkexnews.hk/Shareholding-Disclosures/Stock-Connect-Shareholding
    _date = arrow.get(date).format('YYYY-MM-DD')
    mkt = {'north':"001','003", 'shgt':'001', 'szgt':'003', 'south':'S'}
    params = dict(token='70f12f2f4f091e459a279469fe49eca5', type='HSGTHDSTA',
        st='HDDATE,SHAREHOLDPRICE', sr=3, p=page, ps=count,
        filter="(MARKET in ('%s'))(HDDATE=^%s^)"%(mkt[mkt_type],_date))
    if code:
        params.update({"filter":"(SCODE='%s')"%check_symbol(code)[2:]})
    resp = sess.get(api.margin, params=params)
    df = pd.read_json(resp.text).set_index('HDDATE')\
            .drop(columns=['HKCODE','MARKET','Zb','Zzb'])
    df.index = pd.to_datetime(df.index)
    return df.rename(columns=sheet.hsgt_hold)


def get_trade_days(start_date: str = '-1y', end_date: str = arrow.now(),
                   market: str = 'SSE', frequency: str = '1d'):
    """get trade days for data cleaning. 交易日列表,用于数据清洗

    :param start_date: (optional) start date of the custom return, default is `-1y`.
        value: -nd -nw -nm -ny cyear or YYYY-MM-DD
    :param end_date: (optional) the end date of the results, default is `now`.
    :param market: (optional) market name, default is `SSE`.
        value: NYSE NASDAQ SSE HKEX
    :param frequency: (optional) frequency of date, default is `1d`.
    :return: pd.DatetimeIndex
    """
    begin = str2date(start_date).format('YYYY-MM-DD')
    end = arrow.get(end_date).format('YYYY-MM-DD')
    mkt = mcal.get_calendar(market)
    calendar = mkt.schedule(begin, end)
    return mcal.date_range(calendar, frequency)


def load_index_data(code: str = None):
    """load index data from index.dat file."""
    with gzip.open(api.index_file, 'rt') as f:
        data = re.findall(api.x_index_data, f.read(), re.S)
    dfs = {k: pd.read_csv(StringIO(v), index_col='date',
                parse_dates=True) for k,v in data}
    return dfs.get(code) if code else dfs