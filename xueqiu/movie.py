# -*- coding: utf-8 -*-

"""
xueqiu.movie
~~~~~~~~~~~~

This module implements a maoyan movie api.

:copyright: (c) 2019 by 1dot75cm.
:license: MIT, see LICENSE for more details.
"""

from . import api
from .utils import sess
from lxml import html
import pandas as pd
import numpy as np
import arrow
import json

head = {
    'Origin':'https://piaofang.maoyan.com',
    'Referer':'https://piaofang.maoyan.com',
    'X-Requested-With':''
}


def get_movie_id(search: str):
    resp = sess.get(api.movie_search%search, headers=head)
    tree = html.fromstring(resp.text)
    title = tree.xpath('//article/div/text()')
    mid = tree.xpath('//article/@data-url')
    return [[k.split('/')[-1],v] for k,v in zip(mid,title)]


def get_movie_boxinfo_byid(mid: int):
    """movie box office history data."""
    def process_data(x):
        x = x.find('<')>=0 and x[1:] or x
        if x.find('万')>=0:
            x = float(x[:-1])*10000
        elif x.find('%')>=0:
            x = float(x[:-1])/100
        elif x == '--':
            x = np.nan
        return float(x)
    resp = sess.get(api.movie_history % mid, headers=head)
    tree = html.fromstring(resp.text)
    dt = json.loads(tree.xpath('//script[@id="pageData"]/text()')[0])
    column = [i['name'] for i in dt['boxDatas'][0]['indicatrixs']]
    index = pd.to_datetime([i['showDate'] for i in dt['boxDatas'][0]['data']])
    data = [i['selectData'] for i in dt['boxDatas'][0]['data']]
    df = pd.DataFrame(data, columns=column, index=index).applymap(process_data)
    df[['分账票房','综合票房']] = df[['分账票房','综合票房']].applymap(lambda x:x*10000)
    return {'id':dt['movieId'], 'name':dt['movieName'], 'data':df}


def get_movie_boxinfo_live(date: str = ''):
    """movie box office live data."""
    param = date and {'beginDate':arrow.get(date).format('YYYYMMDD')} or {}
    resp = sess.get(api.movie_live, params=param, headers=head)
    dt = resp.json()['data']
    column = ('id,名称,分账票房,分账票房占比,综合票房,综合票房占比,排片场次,排片占比,'
              '排座占比,场均人次,上座率,综合票价,分账票价,网售占比,猫眼退票人次,猫眼退票率,'
              '大盘退票人次,大盘退票率,观影人数,累计票房,分账累计票房')
    data = [[
        i['movieId'],i['movieName'],i['splitBoxInfo'],i['splitBoxRate'],
        i['boxInfo'],i['boxRate'],i['showInfo'],i['showRate'],i['seatRate'],
        i['avgShowView'],i['avgSeatView'],i['avgViewBox'],i['splitAvgViewBox'],
        i['onlineBoxRate'],i['myRefundNumInfo'],i['myRefundRateInfo'],i['refundViewInfo'],
        i['refundViewRate'],i['viewInfo'],i['sumBoxInfo'],i['splitSumBoxInfo']
    ] for i in dt['list']]
    return {
        'split_total_box': dt['splitTotalBox'],
        'total_box': dt['totalBox'],
        'maoyan_view': dt['crystal']['maoyanViewInfo'],
        'online_view': dt['crystal'].get('onlineViewInfo'),
        'total_view': dt['crystal']['viewInfo'],
        'data': pd.DataFrame(data, columns=column.split(','))
    }