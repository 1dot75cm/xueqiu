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
import requests_cache
import functools
import subprocess
import tempfile
import arrow
import json
import re
import os


def get_cookies_by_domain(domain, lazy):
    domains = domain.find(',')>0 and domain.split(',') or [domain]
    cookies = []
    for domain in domains:
        cookies += [i for i in browsercookie.load()
            if i.domain == domain and i.value or\
               lazy and i.domain.find(domain)>0 and i.value]
    return cookies

def get_cookies(domain: str = 'xueqiu', lazy: bool = True):
    cj = requests.cookies.cookielib.LWPCookieJar(api.cookie_file)
    # load cookies from browser
    [cj.set_cookie(ck) for ck in get_cookies_by_domain(domain, lazy)]
    # load cookies from file
    if os.path.exists(api.cookie_file):
        cj.load(ignore_discard=True, ignore_expires=True)
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

def get_session(sess = '', host: str = api.prefix, expire: int = 3600*24*7):
    sess = sess or requests_cache.CachedSession(expire_after=expire)
    sess.headers['Origin'] = host
    sess.headers['Referer'] = host
    sess.headers['User-Agent'] = UserAgent().random  # Xueqiu Android 11.8.2
    sess.headers['X-Requested-With'] = 'XMLHttpRequest'  # ajax request
    # load cookie from file, browser or selenium
    sess.cookies = get_cookies()
    return sess

def clean_html(tree: str):
    return html.fromstring(tree).text_content()

def check_symbol(code: str, source: str = 'xueqiu'):
    # xueqiu: 美股 FB BABA, 港股 00700 HKHSI, A股 SH601318 SZ000333
    # yahoo: 美股 FB BABA, 港股 0700.HK ^HSI, A股 601318.SS 000333.SZ
    # 163: A股 0601318 1000333
    _code = code
    prefix, suffix = code[:2].lower(), code[-2:].lower()
    match = re.search(r'\d+', str(code))
    if match and len(match[0])>=5:
        code = match[0]
    else:
        code = str(code)
    sym = {'xueqiu': {'sz':'SZ'+code,  'sh':'SH'+code,  'ss':'SH'+code,  'hk':code},
           'yahoo':  {'sz':code+'.SZ', 'sh':code+'.SS', 'ss':code+'.SS', 'hk':code[1:]+'.HK'},
           '163':    {'sz':'1'+code,   'sh':'0'+code,   'ss':'0'+code,   'hk':code}}
    if _code[:3].lower() in ['.sp','csi']:
        return _code
    elif prefix in ['sh','sz']:
        return sym[source].get(prefix)
    elif suffix in ['sh','ss','sz','hk']:
        return sym[source].get(suffix)
    elif len(code) > 5:
        if prefix in ['00','15','16','30','39']:
            return sym[source]['sz']
        elif prefix in ['50','51','60']:
            return sym[source]['sh']
    elif len(code) == 5 and code[0] != '^':
        return sym[source]['hk']
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

def js2obj(jscode: str, objname: str):
    jscode = f"{jscode};console.log(JSON.stringify({objname},null,0))"  # 对象,replacer函数,缩进
    stdout = subprocess.check_output('node', input=jscode.encode())
    return json.loads(stdout)

def str2date(s: str):
    if s[0] != '-' and s != 'cyear':
        return arrow.get(s)
    date = lambda **kw: arrow.now().replace(**kw)
    n, k = s[:-1], s[-1]
    bg = {'d':['days',n],
          'w':['weeks',n],
          'm':['months',n],
          'q':['quarters',n],
          'y':['years',n],
          'c':{'years':-1, 'month':12, 'day':31}}
    if s == 'cyear': return date(**bg['c'])
    return date(**{bg[k][0]: int(bg[k][1])})

def search_invest(query, query_type='quotes'):
    # quotes行情 news新闻 articles分析 ec_event财经日历
    header = {'Origin':api.invest, 'Referer':api.invest}
    form_data = {'search_text':query,'tab':query_type,'offset':0,'limit':270}
    resp = sess.post(api.invest_search, data=form_data, headers=header).json()
    ks = {'quotes': ['pairId','name','symbol','exchange'],
          'news': ['dataID','name','link'],
          'articles': ['dataID','name','link'],
          'ec_event': ['dataID','name']}
    return [[str(i[k]) for k in ks[query_type]] for i in resp.get(query_type)]


exusd = functools.partial(exrate, code="USD")
exhkd = functools.partial(exrate, code="HKD")
sess = get_session()