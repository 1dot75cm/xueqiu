# -*- coding: utf-8 -*-

"""
xueqiu.fund
~~~~~~~~~~~

This module implements some fund apis.

:copyright: (c) 2019 by 1dot75cm.
:license: MIT, see LICENSE for more details.
"""

__all__ = ['get_all_funds', 'get_all_funds_ranking']

from .utils import sess
from .utils import str2date
from .utils import js2obj
from . import api
import pandas as pd
import arrow
import json


def get_all_funds():
    """Get all funds."""
    resp = sess.get(api.all_funds)
    funds = pd.DataFrame(
        json.loads(resp.text[:-1].split('=')[1]),
        columns=['code',1,'name','type',2]).drop(columns=[1,2])
    return funds


def _funds_ranking_subopts(fund_type: str, opt: str = ''):
    # 债券子选项 分类[041长债 042短债 043混债 044定开债 045可转债],杠杆比例[0-100 100-150 150-200 200-99999],,,,
    # 指数子选项 ,,标的[053沪深 054行业 01大盘 02,03中小盘 001股指 003债指],方式[051被动 052增强],,
    # QDII子选项 [311全球 312亚太 313大中华区 314新兴市场 315金砖国家 316成熟市场 317美国股票 318全球指数 319ETF联接 320股债混合 330债券 340商品]
    opts = {'zq': [{'cz':'041','dz':'042','hz':'043','dkz':'044','kzz':'045'},
                   {'0-100':'0-100','100-150':'100-150','150-200':'150-200','200+':'200-99999'}, [0,1]],
            'zs': [{'hs':'053','hy':'054','dp':'01','zxp':'02,03','gz':'001','zz':'003'},
                   {'bd':'051','zq':'052'}, [2,3]],
            'qdii': [{'qqgp':'311','ytgp':'312','dzh':'313','xxsc':'314','jzgj':'315','cssc':'316',
                      'us':'317','qqidx':'318','etf':'319','hh':'320','zq':'330','sp':'340'}, {}, [0,0]]}
    subs = ['']*6
    _opt1, _opt2 = opt and opt.split(',') or ['']*2
    ks = fund_type in opts.keys() and opts[fund_type] or []
    if ks:
        opt1, opt2 = ks[0].get(_opt1,''), ks[1].get(_opt2,'')
        subs[ks[2][0]], subs[ks[2][1]] = opt1, opt2
        return [f'{opt1}|{opt2}', ','.join(subs)]
    return ['', ','*5]


def get_all_funds_ranking(fund_type: str = 'all',
                          start_date: str = '-1y',
                          end_date: str = arrow.now(),
                          sort: str = 'desc',
                          subopts: str = '',
                          available: str = 1):
    """Get all funds ranking from 'fund.eastmoney.com'. (基金排行)

    :param fund_type: (optional) fund type, default is `all`.
        value: ct场内 gp股票 hh混合 zq债券 zs指数 bb保本 qdii lof fof
    :param start_date: (optional) start date of the custom return, default is `-1y`.
        value: -nd -nw -nm -ny cyear or YYYY-MM-DD
    :param end_date: (optional) the end date of the results, default is `now`.
    :param sort: (optional) results order, default is `desc`.
    :param subopts: (optional) some suboptions. format is a list of options(`first,second`).
        Suboptions for bonds(有关债券的子选项):
        - first option is bonds type(债券类型).
            value: cz长债 dz短债 hz混债 dkz定开债 kzz可转债
        - second option is leverage ratio(杠杆比例).
            value: 0-100 100-150 150-200 200+

        Suboptions for stock index(有关指数的子选项):
        - first option is index type(标的).
            value: hs沪深 hy行业 dp大盘 zxp中小盘 gz股指 zz债指
        - second option is stock index operation(运作方式).
            value: bd被动 zq增强

        Suboptions for QDII fonds.
        - first option is fond type(基金类型).
            vaule: qqgp全球股票 ytgp亚太股票 dzh大中华区 xxsc新兴市场 jzgj金砖国家
                   cssc成熟市场 us美国股票  qqidx全球指数 etf hh股债混合 zq债券 sp商品
    :param available: (optional) `1` can buy, `0` including both, default is `1`.
    :return: a list of the funds.
    :rtype: `pd.DataFrame`.
    """
    dtype = fund_type == 'ct' and 'fb' or 'kf'
    begin = str2date(start_date).format('YYYY-MM-DD')
    end = arrow.get(end_date).format('YYYY-MM-DD')
    opt1, opt2 = _funds_ranking_subopts(fund_type, subopts)
    params = dict(op='ph',dt=dtype,ft=fund_type,rs='',gs=0,sc='zzf',st=sort,pi=1,pn=10000)  # 场内基金
    fund_type != 'ct' and params.update(dict(sd=begin,ed=end,qdii=opt1,tabSubtype=opt2,dx=available))
    resp = sess.get(api.all_funds_rank, params=params)
    obj = js2obj(resp.text, 'rankData')
    # dataframe
    if fund_type == 'ct':  # 场内基金
        cols = 'code,name,1,date,nav,cnav,-1week,-1month,-3month,-6month,-1year,-2year,'\
               '-3year,current_year,since_create,issue_date,,,,,,type'
        newcols = cols.replace('1','type,issue_date',1).split(',issue_date,,')[0]
    else:  # 基金排行
        cols = 'code,name,1,date,nav,cnav,percent,-1week,-1month,-3month,-6month,-1year,-2year,'\
               '-3year,current_year,since_create,issue_date,,custom,2,,,,'
        newcols = cols.replace('1','issue_date',1).replace('issue_date,,','').split(',2')[0]
    df = pd.DataFrame([i.split(',')[:-1] for i in obj['datas']],
            columns=cols.split(',')).ffill(None)[newcols.split(',')]
    df['date'] = pd.to_datetime(df['date'])
    df['issue_date'] = pd.to_datetime(df['issue_date'])
    df[['nav','cnav']] = df[['nav','cnav']].applymap(lambda x:x and float(x) or None)
    colnum = fund_type == 'ct'\
        and range(df.columns.get_loc('-1week'), len(df.columns))\
        or  range(df.columns.get_loc('percent'), len(df.columns))
    df.iloc[:,colnum] = df.iloc[:,colnum].applymap(lambda x:x and float(x)/100 or None)
    return df