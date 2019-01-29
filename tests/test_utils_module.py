# -*- coding: utf-8 -*-

import pytest

from xueqiu import api
from xueqiu import utils
from requests.cookies import cookielib


def test_get_cookies():
    cj = utils.get_cookies()
    assert isinstance(cj, cookielib.LWPCookieJar)
    assert cj.filename == api.cookie_file


def test_get_session():
    sess = utils.get_session()
    resp = sess.get(api.prefix)
    assert resp.ok


def test_clean_html():
    html = "<span><a href=''>Hello</a></span>"
    assert utils.clean_html(html) == 'Hello'


def test_check_symbol():
    stock = utils.check_symbol(601318)
    assert stock == "SH601318"
    stock = utils.check_symbol('000651')
    assert stock == "SZ000651"
    stock = utils.check_symbol('00700')
    assert stock == "00700"
    stock = utils.check_symbol('HUYA')
    assert stock == "HUYA"


def test_exrate():
    ex = utils.exrate("2019-01-10", "EUR")
    assert ex == [7.8765, 7.8443]
    ex = utils.exusd(date="2019-01-10")
    assert ex == [6.816, 6.8526]
    ex = utils.exhkd("2019-01-10")
    assert ex == [0.86959, 0.87419]