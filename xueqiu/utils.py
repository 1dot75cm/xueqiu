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
import functools
import arrow
import re
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
        os.makedirs(os.path.dirname(api.cookie_file), exist_ok=True)
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

def check_symbol(code: str):
    code = str(code)
    if len(code) > 5:
        if code[:2] in ["30", "39", "00"]:
            return "SZ" + code
        elif code[:2] in ["60", "50", "51"]:
            return "SH" + code
    return code

def exrate(date: str = "", code: str = "USD"):
    res, ext = [], {}
    ex = {'USD':'美元','EUR':'欧元','JPY':'日元','HKD':'港元','GBP':'英镑','AUD':'澳大利亚元',
          'NZD':'新西兰元','SGD':'新加坡元','CHF':'瑞士法郎','CAD':'加拿大元','MYR':'马来西亚林吉特',
          'RUB':'俄罗斯卢布','ZAR':'南非兰特','KRW':'韩元','AED':'阿联酋迪拉姆','SAR':'沙特里亚尔',
          'HUF':'匈牙利福林','PLN':'波兰兹罗提','DKK':'丹麦克朗','SEK':'瑞典克朗','NOK':'挪威克朗',
          'TRY':'土耳其里拉','MXN':'墨西哥比索','THB':'泰铢'}
    if not date:
        resp = sess.get(api._exrate).json()
        date = arrow.get(resp['data']['lastDate'].split()[0])
    else:
        date = arrow.get(date)
    date = date.weekday()>4 and date.shift(weeks=-1,weekday=4) or date
    for dt in date,date.shift(days=-1):
        resp = sess.get(api.exrate % dt.format("YYYY-MM-DD")).json()
        price = re.findall(api.x_exrate, resp['data']['vo']['price'])
        for k,v in zip(ex.keys(), price):
            ext.update({k:float(v)})
        res.append(ext[code])
    return res


exusd = functools.partial(exrate, code="USD")
exhkd = functools.partial(exrate, code="HKD")
sess = get_session()