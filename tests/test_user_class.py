# -*- coding: utf-8 -*-

import pytest

from xueqiu import api
from xueqiu import User
from xueqiu import Post
from xueqiu import Stock


@pytest.fixture(scope='module')
def setup_module(request):
    def teardown_module():
        pass
    request.addfinalizer(teardown_module)
    global u, uid
    uid = 2478797769
    u = User(uid)


def test_init(setup_module):
    assert u.id == uid
    assert u.profile == f"{api.prefix}/u/{uid}"
    assert u.name == "红利基金"
    assert u.city == "上海不限"
    assert isinstance(u.friends_count, int)
    assert isinstance(u.followers_count, int)
    assert isinstance(u.posts_count, int)
    assert isinstance(u.stocks_count, int)
    assert repr(u) == "<xueqiu.User 红利基金(2478797769)>"
    assert u.__str__() == "红利基金(2478797769)"


def test_get_friends(setup_module):
    assert u.friends == {}
    u.get_friends(page=2)
    assert u.friends['page'] == 2
    assert isinstance(u.friends['list'][0], User)


def test_get_followers(setup_module):
    assert u.followers == {}
    u.get_followers(page=2)
    assert u.followers['page'] == 2
    assert isinstance(u.followers['list'][0], User)


def test_get_posts(setup_module):
    assert u.posts == {}
    u.get_posts(page=2)
    assert u.posts['page'] == 2
    assert isinstance(u.posts['list'][0], Post)


def test_get_articles(setup_module):
    assert u.articles == {}
    u.get_articles(page=2)
    assert u.articles['page'] == 2
    assert isinstance(u.articles['list'][0], Post)


def test_get_favorites(setup_module):
    assert u.favorites == {}
    u.get_favorites()
    assert u.favorites['page'] == 1
    assert isinstance(u.favorites['list'][0], Post)


def test_get_stocks(setup_module):
    assert u.stocks == {}
    u.get_stocks(count=20)
    assert u.stocks['count'] == 20
    assert isinstance(u.stocks['list'][0], Stock)


def test_get_hot_stocks(setup_module):
    assert u.hot_stocks == {}
    u.get_hot_stocks()
    assert isinstance(u.hot_stocks['list'][0], Stock)