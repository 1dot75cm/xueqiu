# -*- coding: utf-8 -*-

import pytest

from xueqiu import api
from xueqiu import Selector
from xueqiu import Stock


@pytest.fixture(scope='module')
def setup_module(request):
    def teardown_module():
        pass
    request.addfinalizer(teardown_module)
    global s
    s = Selector("SH")


def test_init(setup_module):
    assert s.market == "SH"
    assert repr(s) == "<xueqiu.Selector {}?category=SH&exchange=&indcode=&areacode=&orderby=" \
                      "symbol&order=desc&current=ALL&pct=ALL&page=1&size=10>".format(api.selector)
    assert s.__str__() == "{}?category=SH&exchange=&indcode=&areacode=&orderby=symbol&order=" \
                          "desc&current=ALL&pct=ALL&page=1&size=10".format(api.selector)


def test_help(setup_module):
    assert 'pettm' in s.help('base',show='keys')
    assert 'follow7d' in s.help('ball',show='keys')
    assert 'current' in s.help('quota',show='keys')
    assert 'tag' in s.help('finan_rate',show='keys')
    assert 'evps' in s.help('stock_data',show='keys')
    assert 'bp' in s.help('profit_sheet',show='keys')
    assert 'up' in s.help('balance_sheet',show='keys')
    assert 'fncf' in s.help('cash_sheet',show='keys')


def test_scope(setup_module):
    assert 'SZ' in s.scope('SZ','K70','CN330000').url()
    assert 'K70' in s.scope('SZ','K70','CN330000').url()
    assert 'CN330000' in s.scope('SZ','K70','CN330000').url()


def test_param(setup_module):
    s.param('mc', roediluted_20180930='0_30')
    assert "mc=ALL" in s.url()
    assert "roediluted.20180930=0_30" in s.url()


def test_orderby(setup_module):
    s.orderby('mc')
    assert "orderby=mc" in s.url()


def test_order(setup_module):
    s.order('asc')
    assert "order=asc" in s.url()


def test_page(setup_module):
    s.page(2)
    assert "page=2" in s.url()


def test_count(setup_module):
    s.count(2)
    assert "size=2" in s.url()


def test_run(setup_module):
    isinstance(s.run()['list'][0], Stock)