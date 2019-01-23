# -*- coding: utf-8 -*-

"""
xueqiu.utils
~~~~~~~~~~~~

This module contains some utils.

:copyright: (c) 2019 by 1dot75cm.
:license: MIT, see LICENSE for more details.
"""

__all__ = ['get_session', 'clean_html', 'sess']

from . import api
from lxml import html
from fake_useragent import UserAgent
from selenium import webdriver
import requests
import os


def get_session():
    sess = requests.sessions.Session()
    sess.headers['Host'] = api.host
    sess.headers['Origin'] = api.prefix
    sess.headers['Referer'] = api.prefix
    sess.headers['User-Agent'] = UserAgent().random
    # cookies
    opts = webdriver.ChromeOptions()
    opts._arguments = ['--disable-gpu', '--headless', '--remote-debugging-port=9090']
    with webdriver.Chrome(options=opts) as browser:
        browser.get(api.prefix)
        #sess.cookies = requests.utils.cookiejar_from_dict(
        #    {i['name']: i['value'] for i in browser.get_cookies()},
        #    requests.cookies.cookielib.LWPCookieJar(api.cookie_file))
        sess.cookies = requests.cookies.cookielib.LWPCookieJar(api.cookie_file)
        for i in browser.get_cookies():
            sess.cookies.set_cookie(
                requests.cookies.create_cookie(i['name'], i['value'],
                    domain=i.get('domain'), expires=i.get('expiry') or None,
                    rest={'HttpOnly':i.get('httpOnly')}, path='/'))
    # cookie directory
    if not os.path.exists(os.path.dirname(api.cookie_file)):
        os.mkdir(os.path.dirname(api.cookie_file))
    return sess

def clean_html(tree: str):
    return html.fromstring(tree).text_content()


sess = get_session()