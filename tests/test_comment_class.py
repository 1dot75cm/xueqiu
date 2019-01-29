# -*- coding: utf-8 -*-

import pytest

from xueqiu import Post
from xueqiu import Comment


@pytest.fixture(scope='module')
def setup_module(request):
    def teardown_module():
        pass
    request.addfinalizer(teardown_module)
    global c, p, pid
    pid = '2478797769/78869335'
    p = Post(pid)
    p.get_comments()
    c = p.comments['list'][0]


def test_init(setup_module):
    assert isinstance(c, Comment)
    assert c.id
    assert c.user.name
    assert c.post.id == 78869335
    assert c.created_at
    assert c.like_count >= 0
    assert c.text