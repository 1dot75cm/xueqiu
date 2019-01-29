# -*- coding: utf-8 -*-

import pytest

from xueqiu import Fund
from xueqiu import Stock


@pytest.fixture(scope='module')
def setup_module(request):
    def teardown_module():
        pass
    request.addfinalizer(teardown_module)
    global f, fid
    fid = '501301'
    f = Fund(fid)


def test_init(setup_module):
    assert f.symbol == "SH501301"
    assert isinstance(f.fund_nav[1], float)
    assert repr(f) == "<xueqiu.Fund 香港大盘[SH501301]>"
    assert f.__str__() == "香港大盘[SH501301]"


def test_get_fund_stocks(setup_module):
    f.get_fund_stocks()
    assert isinstance(f.fund_stocks[0], Stock)
    assert isinstance(f.fund_weight[0], float)


def test_get_fund_histories(setup_module):
    f.get_fund_histories()
    assert isinstance(f.fund_history['df']['nav'][0], str)