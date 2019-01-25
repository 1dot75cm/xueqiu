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
import browsercookie
import requests
import os


def get_cookies():
    cj = requests.cookies.cookielib.LWPCookieJar(api.cookie_file)
    cookies = [i for i in browsercookie.load() if i.domain.find("xueqiu")>0]
    # load cookies from file
    if os.path.exists(api.cookie_file):
        cj.load(ignore_discard=True, ignore_expires=True)
    # load cookies from browser
    elif len(cookies) > 5:
        [cj.set_cookie(ck) for ck in cookies]
    # load cookies from selenium
    else:
        opts = webdriver.ChromeOptions()
        opts._arguments = ['--disable-gpu', '--headless', '--remote-debugging-port=9090']
        browser = webdriver.Chrome(options=opts)
        browser.get(api.prefix)
        for i in browser.get_cookies():
            cj.set_cookie(requests.cookies.create_cookie(i['name'], i['value'],
                domain=i.get('domain'), expires=i.get('expiry') or None,
                rest={'HttpOnly':i.get('httpOnly')}, path='/'))
        browser.close()
    # cookie directory
    if not os.path.exists(os.path.dirname(api.cookie_file)):
        os.mkdir(os.path.dirname(api.cookie_file))
    return cj

def get_session():
    sess = requests.sessions.Session()
    sess.headers['Origin'] = api.prefix
    sess.headers['Referer'] = api.prefix
    sess.headers['User-Agent'] = UserAgent().random  # Xueqiu Android 11.8.2
    sess.headers['X-Requested-With'] = 'XMLHttpRequest'  # ajax request
    # load cookie from file, browser or selenium
    sess.cookies = get_cookies()
    return sess

def clean_html(tree: str):
    return html.fromstring(tree).text_content()


sess = get_session()