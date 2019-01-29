# -*- coding: utf-8 -*-

import pytest

from xueqiu import api
from xueqiu import Post
from xueqiu import Comment


@pytest.fixture(scope='module')
def setup_module(request):
    def teardown_module():
        pass
    request.addfinalizer(teardown_module)
    global p, pid
    pid = '2478797769/78869335'
    p = Post(pid)


def test_init(setup_module):
    assert p.id == 78869335
    assert p.user.name == "红利基金"
    assert p.created_at.format("YYYY-MM-DD") == "2016-12-13"
    assert p.target == api.prefix +'/'+ pid
    assert p.view_count >= 0
    assert p.reply_count >= 0
    assert p.retweet_count >= 0
    assert p.fav_count >= 0
    assert p.like_count >= 0
    assert isinstance(p.title, str)
    assert repr(p) == f"<xueqiu.Post 【你了解红利基金吗】红利基金（50102[{p.target}]>"
    assert p.__str__() == f"【你了解红利基金吗】红利基金（50102, {p.target}"


def test_get_content(setup_module):
    assert not p.full_text
    p.get_content()
    assert p.full_text


def test_get_comments(setup_module):
    assert not p.comments
    p.get_comments()
    assert isinstance(p.comments['list'][0], Comment)