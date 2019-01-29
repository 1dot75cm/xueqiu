# -*- coding: utf-8 -*-

import pytest

from xueqiu.model import create_or_refresh_stocks
from xueqiu import news
from xueqiu import search
from xueqiu import Post


def test_search():
    # search stock
    s = search("中国平安")
    assert s['list'][0].name == "中国平安"
    # search post
    p = search("你了解红利基金吗", query_type="post")
    assert isinstance(p['list'][0], Post)
    # search user
    u = search("红利基金", query_type="user")
    assert u['list'][0].name == "红利基金"


def test_news():
    assert isinstance(news()['list'][0], Post)


def test_create_or_refresh_stocks():
    stocks = ['601318', '000333', '00700', 'TSLA', 'RHT']
    s = create_or_refresh_stocks(stocks)
    assert s[0].name == "中国平安"
    assert s[1].name == "美的集团"
    assert s[2].name == "腾讯控股"
    assert s[3].name == "特斯拉"
    assert s[4].name == "红帽"