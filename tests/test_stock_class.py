# -*- coding: utf-8 -*-

import pytest

from xueqiu import User
from xueqiu import Post
from xueqiu import Stock


@pytest.fixture(scope='module')
def setup_module(request):
    def teardown_module():
        pass
    request.addfinalizer(teardown_module)
    global s, sid
    sid = "SH601318"
    s = Stock(sid)


def test_init(setup_module):
    assert s.symbol == sid
    assert s.code == sid[2:]
    assert s.name == "中国平安"
    assert isinstance(s.current, float)
    assert isinstance(s.current_year_percent, float)
    assert isinstance(s.percent, float)
    assert isinstance(s.chg, float)
    assert isinstance(s.open, float)
    assert isinstance(s.last_close, float)
    assert isinstance(s.high, float)
    assert isinstance(s.low, float)
    assert isinstance(s.avg_price, float)
    assert isinstance(s.volume, int)
    assert isinstance(s.amount, float)
    assert isinstance(s.turnover_rate, float)
    assert isinstance(s.amplitude, float)
    assert isinstance(s.market_capital, float)
    assert isinstance(s.float_market_capital, float)
    assert isinstance(s.total_shares, int)
    assert isinstance(s.float_shares, int)
    assert s.currency == "CNY"
    assert s.exchange == "SH"
    assert s.issue_date.format("YYYY-MM-DD") == "2007-02-28"
    assert repr(s) == "<xueqiu.Stock 中国平安[SH601318]>"
    assert s.__str__() == "中国平安[SH601318]"


def test_refresh(setup_module):
    time = s.time
    s.refresh()
    assert s.time != time


def test_get_posts(setup_module):
    assert s.posts == {}
    s.get_posts(page=2)
    assert s.posts['page'] == 2
    assert isinstance(s.posts['list'][0], Post)


def test_get_followers(setup_module):
    assert s.followers == {}
    s.get_followers(page=2)
    assert s.followers['page'] == 2
    assert isinstance(s.followers['list'][0], User)


def test_get_prousers(setup_module):
    assert s.prousers == {}
    s.get_prousers()
    assert isinstance(s.prousers[0], User)


def test_get_popstocks(setup_module):
    assert s.popstocks == []
    s.get_popstocks()
    assert isinstance(s.popstocks[0], Stock)


def test_get_industry_stocks(setup_module):
    assert s.industries == {}
    s.get_industry_stocks()
    assert isinstance(s.industries['list'][0], Stock)


def test_get_histories(setup_module):
    assert s.history == {}
    s.get_histories('2019-01-07','2019-01-11')
    assert s.history['close'][0] == 56.30