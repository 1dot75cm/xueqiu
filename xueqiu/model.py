# -*- coding: utf-8 -*-

"""
xueqiu.model
~~~~~~~~~~~~

This module implements a humanize XueQiu API wrappers.

:copyright: (c) 2019 by 1dot75cm.
:license: MIT, see LICENSE for more details.
"""

__all__ = ['news', 'search', 'Selector', 'Stock', 'Fund', 'Post', 'Comment', 'User',
           'get_all_funds', 'get_all_funds_ranking', 'get_economic', 'get_economic_of_china']

from .utils import clean_html
from .utils import check_symbol
from .utils import sess
from .utils import str2date
from .utils import js2obj
from . import api
from . import sheet
from lxml import etree
from urllib.parse import urlencode
from urllib.parse import urljoin
import pandas_datareader.data as web
import pandas as pd
import numpy as np
import arrow
import browsercookie
import json
import os
import re


def search(query: str = "",
           query_type: str = "stock",
           symbol: str = "",
           count: int = 10,
           page: int = 1,
           sort: str = "time",
           source: str = "user"):
    """Sends a search request.

    :param query: query string.
    :param query_type: (optional) type of the query request, default is `stock`.
                value: stock, post, user
    :param symbol: (optional) the stock symbol.
    :param count: (optional) the number of results, default is `20`.
    :param page: (optional) page number, default is `1`.
    :param sort: (optional) order type, default is `time`.
                value: time最新, reply评论, relevance默认
    :param source: (optional) source of the results, default is `user`.
                value: all, user讨论, news新闻, notice公告, trans交易
    :return: a list of :class:`Object <instance_id>` objects.
                Object class: Stock, Post or User
    :rtype: list([ins1, ins2, ...])
    """
    # search_post 1.搜索帖子, 2.symbol列出股票帖子
    qapi = {
        'stock': [api.search_stock % (query, count, page), 'stocks'],
        'post': [api.search_post % (query, symbol, count, page, sort, source), 'list'],
        'user': [api.search_user % (query, count, page), 'users'],
    }
    resp = sess.get( qapi[query_type][0] )
    dt = resp.ok and resp.json()
    # stock: q, page, size, stocks
    # post: q, about, count, recommend_cards, page, list, maxPage, key, facets
    # user: q, pager, count, maxPage, key, users
    return {
        'count': dt.get('count'),
        'page': page,
        'maxpage': dt.get('maxPage'),
        'list': [eval(query_type.title())(i)
                    for i in dt[qapi[query_type][1]]]
    }


def news(category: int = -1, count: int = 10, max_id: int = -1):
    """Get news.

    :param category: (optional) type of the news, default is `-1`.
                value: 头条-1, 今日话题0, 直播6, 沪深105, 港股102, 美股101,
                    基金104, 私募113, 房产111, 汽车114, 保险110
    :param count: (optional) the number of results, default is `10`.
    :param max_id: (optional) the max id of news, default is `-1`.
    :return: a list of :class:`Post <instance_id>` objects.
    :rtype: list([post1, post2, ...])
    """
    global _next_max_id
    max_id = globals().get("_next_max_id") and _next_max_id or max_id
    resp = sess.get(api.news % (max_id, category, count))
    dt = resp.ok and resp.json()
    _next_max_id = dt['next_max_id']
    return {
        'list': [Post(json.loads(i['data'])) for i in dt['list']],
        'next_max_id': _next_max_id
    }


def create_or_refresh_stocks(stocks: list):
    """Create or refresh stocks.

    :param stocks: the list contains a stock symbol or Stock object.
    :return: a list of :class:`Stock <instance_id>` objects.
    :rtype: [Stock1, Stock2, ...]
    """
    dot_stock = isinstance(stocks[0], Stock) and \
                ",".join([i.symbol for i in stocks]) or \
                ",".join([check_symbol(i) for i in stocks])  # symbol or Stock
    resp = sess.get(api.stocks_quote_v5 % dot_stock)
    dt = resp.ok and resp.json()['data']
    if isinstance(stocks[0], Stock):
        [stocks[i].refresh(v) for i,v in enumerate(dt['items'])]
        return stocks
    return [Stock(i['quote']) for i in dt['items']]


def get_all_funds():
    """Get all funds."""
    resp = sess.get(api.all_funds)
    funds = pd.DataFrame(
        json.loads(resp.text[:-1].split('=')[1]),
        columns=['code',1,'name','type',2]).drop(columns=[1,2])
    return funds

def _funds_ranking_subopts(fund_type: str, opt: str = ''):
    # 债券子选项 分类[041长债 042短债 043混债 044定开债 045可转债],杠杆比例[0-100 100-150 150-200 200-99999],,,,
    # 指数子选项 ,,标的[053沪深 054行业 01大盘 02,03中小盘 001股指 003债指],方式[051被动 052增强],,
    # QDII子选项 [311全球 312亚太 313大中华区 314新兴市场 315金砖国家 316成熟市场 317美国股票 318全球指数 319ETF联接 320股债混合 330债券 340商品]
    opts = {'zq': [{'cz':'041','dz':'042','hz':'043','dkz':'044','kzz':'045'},
                   {'0-100':'0-100','100-150':'100-150','150-200':'150-200','200+':'200-99999'}, [0,1]],
            'zs': [{'hs':'053','hy':'054','dp':'01','zxp':'02,03','gz':'001','zz':'003'},
                   {'bd':'051','zq':'052'}, [2,3]],
            'qdii': [{'qqgp':'311','ytgp':'312','dzh':'313','xxsc':'314','jzgj':'315','cssc':'316',
                      'us':'317','qqidx':'318','etf':'319','hh':'320','zq':'330','sp':'340'}, {}, [0,0]]}
    subs = ['']*6
    _opt1, _opt2 = opt and opt.split(',') or ['']*2
    ks = fund_type in opts.keys() and opts[fund_type] or []
    if ks:
        opt1, opt2 = ks[0].get(_opt1,''), ks[1].get(_opt2,'')
        subs[ks[2][0]], subs[ks[2][1]] = opt1, opt2
        return [f'{opt1}|{opt2}', ','.join(subs)]
    return ['', ','*5]

def get_all_funds_ranking(fund_type: str = 'all',
                          start_date: str = '-1y',
                          end_date: str = arrow.now(),
                          sort: str = 'desc',
                          subopts: str = '',
                          available: str = 1):
    """Get all funds ranking from 'fund.eastmoney.com'. (基金排行)

    :param fund_type: (optional) fund type, default is `all`.
        value: ct场内 gp股票 hh混合 zq债券 zs指数 bb保本 qdii lof fof
    :param start_date: (optional) start date of the custom return, default is `-1y`.
        value: -nd -nw -nm -ny cyear or YYYY-MM-DD
    :param end_date: (optional) the end date of the results, default is `now`.
    :param sort: (optional) results order, default is `desc`.
    :param subopts: (optional) some suboptions. format is a list of options(`first,second`).
        Suboptions for bonds(有关债券的子选项):
        - first option is bonds type(债券类型).
            value: cz长债 dz短债 hz混债 dkz定开债 kzz可转债
        - second option is leverage ratio(杠杆比例).
            value: 0-100 100-150 150-200 200+

        Suboptions for stock index(有关指数的子选项):
        - first option is index type(标的).
            value: hs沪深 hy行业 dp大盘 zxp中小盘 gz股指 zz债指
        - second option is stock index operation(运作方式).
            value: bd被动 zq增强

        Suboptions for QDII fonds.
        - first option is fond type(基金类型).
            vaule: qqgp全球股票 ytgp亚太股票 dzh大中华区 xxsc新兴市场 jzgj金砖国家
                   cssc成熟市场 us美国股票  qqidx全球指数 etf hh股债混合 zq债券 sp商品
    :param available: (optional) `1` can buy, `0` including both, default is `1`.
    :return: a list of the funds.
    :rtype: `pd.DataFrame`.
    """
    dtype = fund_type == 'ct' and 'fb' or 'kf'
    begin = len(start_date)>5 and arrow.get(start_date).format('YYYY-MM-DD') \
                              or  str2date(start_date).format('YYYY-MM-DD')
    end = arrow.get(end_date).format('YYYY-MM-DD')
    opt1, opt2 = _funds_ranking_subopts(fund_type, subopts)
    params = dict(op='ph',dt=dtype,ft=fund_type,rs='',gs=0,sc='zzf',st=sort,pi=1,pn=10000)  # 场内基金
    fund_type != 'ct' and params.update(dict(sd=begin,ed=end,qdii=opt1,tabSubtype=opt2,dx=available))
    resp = sess.get(api.all_funds_rank, params=params)
    obj = js2obj(resp.text, 'rankData')
    # dataframe
    if fund_type == 'ct':  # 场内基金
        cols = 'code,name,1,date,nav,cnav,-1week,-1month,-3month,-6month,-1year,-2year,'\
               '-3year,current_year,since_create,issue_date,,,,,,type'
        newcols = cols.replace('1','type,issue_date',1).split(',issue_date,,')[0]
    else:  # 基金排行
        cols = 'code,name,1,date,nav,cnav,percent,-1week,-1month,-3month,-6month,-1year,-2year,'\
               '-3year,current_year,since_create,issue_date,,custom,2,,,,'
        newcols = cols.replace('1','issue_date',1).replace('issue_date,,','').split(',2')[0]
    df = pd.DataFrame([i.split(',')[:-1] for i in obj['datas']],
            columns=cols.split(',')).ffill(None)[newcols.split(',')]
    df['date'] = pd.to_datetime(df['date'])
    df['issue_date'] = pd.to_datetime(df['issue_date'])
    df[['nav','cnav']] = df[['nav','cnav']].applymap(lambda x:x and float(x) or None)
    colnum = fund_type == 'ct'\
        and range(df.columns.get_loc('-1week'), len(df.columns))\
        or  range(df.columns.get_loc('percent'), len(df.columns))
    df.iloc[:,colnum] = df.iloc[:,colnum].applymap(lambda x:x and float(x)/100 or None)
    return df


def get_economic(name: str = 'help', search: str = '中国'):
    """Get economic data from investing.com."""
    form_data = {'search_text':search,'tab':'ec_event','offset':0,'limit':270}
    resp = sess.post(api.economic_search, data=form_data)
    events = {i['name']:i['dataID'] for i in resp.json()['ec_event']}
    if name == 'help': return events
    elif name in events.keys() or isinstance(int(name), int):
        resp = sess.get(api.economic % (events.get(name) or name))
        cols = ['timestamp','actual','actual_state','forecast','revised']
        df = pd.DataFrame(resp.json()['attr'])[cols]
        df['date'] = df['timestamp'].apply(lambda x:arrow.get(x/1000).datetime)
        return df.set_index('date').drop('timestamp',axis=1)


def get_economic_of_china(indicator: str = 'help',
                          region: str = '',
                          category: str = 'year',
                          search: str = '',
                          time_period: str = ''):
    """Get economic data of china from data.stats.gov.cn.

    :param indicator: (optional) economic indicators, default is `help`.
    :param region: (optional) region, used to `state` and `city` categories only.
    :param category: (optional) category of economic indicators, default is `year`.
        value: month quarter year month_by_state quarter_by_state
            year_by_state month_by_city year_by_city
    :param search: (optional) search indicators, default is `''`.
    :param time_period: (optional) period of time, default is `''`.
        value: month: 201810,201812 201801-201809
               quarter: 2018A,2018B,2018C,2018D
               year: 2017,2018 2016-2018
               other: 2014-,last5
    :return: the economic data of china.
    :rtype: `pd.DataFrame`.
    """
    process_month = lambda x:x[:4]+'-'+x[4:]
    process_quarter = lambda x:x[:-1]+dict(A='Q1',B='Q2',C='Q3',D='Q4')[x[-1]]
    cg = {'month': ['A01','hgyd',process_month],
          'quarter': ['B01','hgjd',process_quarter],
          'year': ['C01','hgnd',lambda x:x],
          'month_by_state': ['E0101','fsyd',process_month],
          'quarter_by_state': ['E0102','fsjd',process_quarter],
          'year_by_state': ['E0103','fsnd',lambda x:x],
          'month_by_city': ['E0104','csyd',process_month],
          'year_by_city': ['E0105','csnd',process_quarter]}
    # search indicators
    def _search(s):
        if s == 'region':
            tree = cg[category][1] == 'csnd' and '000000' or '00'
            data = dict(m='findZbXl',db=cg[category][1],wd='reg',treeId=tree)
        else:
            data = dict(m='findGjcx',db=cg[category][1],wd='zb',s=s)
        resp = sess.post(api.china_stats_adv, data=data)
        return [{'id':i['id'],'name':i['name']} for i in resp.json()]
    if search: return _search(search)
    if indicator == 'help': return 'please add search param.'
    # get data
    inds, regs = indicator.split(','), region.split(',')  # list
    query = [{"wd":"zb","zb":inds}]
    category in list(cg.keys())[-5:] and query.append({"wd":"reg","zb":regs})  # region
    data = {'c': json.dumps(query)}
    params = {'m':'advquery','cn':cg[category][0]}
    sess.post(api.china_stats_adv, params=params, data=data)
    ## region options ##
    _reg = {'wds':[], 'row':'zb', 'idx':0}  # region 默认
    if category in list(cg.keys())[-5:] and len(regs)>=2:  # region 多个地区，一个指标
        _reg = {'wds':[{"wdcode":"zb","valuecode":inds[0]}], 'row':'reg', 'idx':1}
    elif category in list(cg.keys())[-5:] and len(regs)<2:  # region 多个指标，一个地区
        _reg = {'wds':[{"wdcode":"reg","valuecode":regs[0]}], 'row':'zb', 'idx':0}
    ## end region options ##
    params = dict(m='QueryData',dbcode=cg[category][1],rowcode=_reg['row'],colcode='sj',
        wds=json.dumps(_reg['wds']), dfwds=json.dumps([{"wdcode":"sj","valuecode":time_period}]))
    resp = sess.get(api.china_stats, params=params).json()['returndata']
    # dataframe
    index = [cg[category][2](i['code']) for i in resp['wdnodes'][-1]['nodes']]  # 时间
    ck = {i['code']:i['name'] for i in resp['wdnodes'][_reg['idx']]['nodes']}
    data = {i:[] for i in ck.values()}
    for i in resp['datanodes']:
        data[ck[i['wds'][_reg['idx']]['valuecode']]].append(i['data']['data'])
    return pd.DataFrame(data, index=pd.to_datetime(index))


def get_data_yahoo(symbol: str, start: str = '-1y', end: str = None,
                   session = sess, **kwargs):
    """a yahoo stock api wrapper.

    :param symbol: stock symbol or code.
    :param start: (optional) start date of the custom return, default is `-1y`.
        value: -nd -nw -nm -ny cyear or YYYY-MM-DD
    :param end: (optional) the end date of the results, default is `now`.
    :param session: (optional) use an existing session, default is `sess`.
    :param **kwargs: please see `pandas_datareader.data.DataReader` reference.
    :return: pd.DataFrame
    """
    begin = len(start)>5 and arrow.get(start).format('YYYY-MM-DD') \
                         or  str2date(start).format('YYYY-MM-DD')
    df = web.get_data_yahoo(check_symbol(symbol,'yahoo'), start=begin,
            end=end, session=session, **kwargs)
    return df

def get_quote_yahoo(symbol: str, session = sess, **kwargs):
    """get stock summary from yahoo.com."""
    symbol = check_symbol(symbol,'yahoo')
    return web.get_quote_yahoo(symbol, session=session, **kwargs)


def get_stock_margin(code: str = '', begin: str = '-3m', page: int = 1, mkt_type: str = 'all'):
    """get stock margin. 融资融券"""
    begin = len(begin)>5 and arrow.get(begin) or str2date(begin)
    count = (arrow.now()-begin).days
    mkt = {'sh':['HS',"(market='SH')"], 'sz':['HS',"(market='SZ')"], 'all':['LS','']}
    params = dict(token='70f12f2f4f091e459a279469fe49eca5', st='tdate', sr=-1, p=page, ps=count) #js={pages:(tp),data:(x)}
    stock_param = dict(type='RZRQ_DETAIL_NJ', filter='(scode=%s)'%check_symbol(code)[2:])
    mkt_param = dict(type='RZRQ_%sTOTAL_NJ'%mkt[mkt_type][0], filter=mkt[mkt_type][1], mk_time=1)
    params.update(code and stock_param or mkt_param)
    resp = sess.get(api.margin, params=params)
    df = pd.read_json(resp.text).set_index('tdate')
    df.index = pd.to_datetime(df.index)
    return df.rename(columns=sheet.margin)


def get_hsgt_history(mkt_type: str = 'shgt', begin: str = '-1m', page: int = 1):
    """get shanghai-shenzhen-hongkong stock history. 沪深港通历史数据"""
    begin = len(begin)>5 and arrow.get(begin) or str2date(begin)
    count = (arrow.now()-begin).days
    mkt = {'shgt':1, 'szgt':3, 'hksh':2, 'hksz':4}
    params = dict(token='70f12f2f4f091e459a279469fe49eca5', type='HSGTHIS',
        st='DetailDate', sr=-1, p=page, ps=count, filter='(MarketType=%s)'%mkt[mkt_type])
    resp = sess.get(api.margin, params=params)
    df = pd.read_json(resp.text).set_index('DetailDate')
    df.index = pd.to_datetime(df.index)
    return df.rename(columns=sheet.hsgt)

def get_hsgt_top10(mkt_type: str = 'shgt', date: str = arrow.now()):
    """get shanghai-shenzhen-hongkong top10 stock. 沪深港通top10"""
    _date = arrow.get(date).format('YYYY-MM-DD')
    mkt = {'shgt':[1,'hgt'], 'szgt':[3,'sgt'], 'hksh':[2,'ggt'], 'hksz':[4,'ggt']}
    params = dict(token='70f12f2f4f091e459a279469fe49eca5', type='HSGTCJB',
        sty=mkt[mkt_type][1], st='', sr=-1, page=1, pagesize=50,
        filter='(MarketType=%s)(DetailDate=^%s^)'%(mkt[mkt_type][0], _date))
    resp = sess.get(api.margin, params=params)
    df = pd.read_json(resp.text).drop(columns=['MarketType','DetailDate'])
    if mkt_type == 'hksh':
        df = df.drop(columns=['GGTSCJJE','GGTSJME','GGTSMCJE','GGTSMRJE','Rank1'])
    elif mkt_type == 'hksz':
        df = df.drop(columns=['GGTHCJJE','GGTHJME','GGTHMCJE','GGTHMRJE','Rank'])
        df = df.rename({'Rank1':'Rank'}, axis=1)
    else:
        df = df.drop(columns='Rank1')
    return df.set_index('Rank').sort_index()

def get_hsgt_holding(code: str = '', mkt_type: str = 'north', date: str = arrow.now(),
                     page: int = 1, count: int = 50):
    """get shanghai-shenzhen-hongkong stock holding. 沪深港通持股"""
    #沪港通及深港通持股纪录查询服务
    #http://sc.hkexnews.hk/TuniS/www2.hkexnews.hk/Shareholding-Disclosures/Stock-Connect-Shareholding
    _date = arrow.get(date).format('YYYY-MM-DD')
    mkt = {'north':"001','003", 'shgt':'001', 'szgt':'003', 'south':'S'}
    params = dict(token='70f12f2f4f091e459a279469fe49eca5', type='HSGTHDSTA',
        st='HDDATE,SHAREHOLDPRICE', sr=3, p=page, ps=count,
        filter="(MARKET in ('%s'))(HDDATE=^%s^)"%(mkt[mkt_type],_date))
    if code:
        params.update({"filter":"(SCODE='%s')"%check_symbol(code)[2:]})
    resp = sess.get(api.margin, params=params)
    df = pd.read_json(resp.text).set_index('HDDATE')\
            .drop(columns=['HKCODE','MARKET','Zb','Zzb'])
    df.index = pd.to_datetime(df.index)
    return df.rename(columns=sheet.hsgt_hold)


class Comment:
    """A user-created :class:`Comment <instance_id>` object.

    :param dt: the dictionary contains comment data.
    """

    def __init__(self, dt: dict, post):
        self.id = dt['id']
        self.user = User(dt['user'])
        self.post = isinstance(post, Post) and post
        self.created_at = arrow.get(dt['created_at']/1000)
        self.like_count = dt['like_count']
        self.text = clean_html(dt["text"])

    def __repr__(self):
        return "<xueqiu.Comment %s[%s]>" % (self.user.name[:5], self.text[:10])

    def __str__(self):
        return "%s: %s" % (self.user.name, self.text)

    def _set_like(self, apiurl: str = api.comment_like):
        """like or unlike the comment."""
        data = {'id': self.id}
        dt = sess.post(apiurl, data=data).json()
        return dt.get('success') or False

    def like(self):
        """like the comment. (require login)"""
        return self._set_like(api.comment_like)

    def unlike(self):
        """unlike the comment. (require login)"""
        return self._set_like(api.comment_unlike)


class Post:
    """A user-created :class:`Post <instance_id>` object.

    :param dt: the dictionary contains article data.
    """

    def __init__(self, dt: dict):
        if isinstance(dt, str):
            resp = sess.get(urljoin(api.prefix, dt))
            tree = etree.HTML(resp.text).xpath(api.x_post_json)[0]
            dt = json.loads(re.search("= ({.*});", tree).group(1))

        self.id = dt['id']
        self.user = User(dt.get('user') or dt.get('user_id'))
        self.created_at = arrow.get(dt['created_at']/1000)
        self.target = urljoin(api.prefix, dt['target'])  # 文章url
        self.view_count = dt.get('view_count')   # 访问量
        self.reply_count = dt.get('reply_count') # 评论数
        self.retweet_count = dt.get('retweet_count')  # 转发数
        self.fav_count = dt.get('fav_count')     # 收藏数
        self.like_count = dt.get('like_count')   # 点赞数
        self.title = dt.get('title') and clean_html(dt.get('title'))
        self.text = clean_html(dt.get('text') or dt.get('description'))
        self.full_text = ""
        self.comments = {}

    def __repr__(self):
        return "<xueqiu.Post %s[%s]>" % (self.title[:20], self.target)

    def __str__(self):
        return "%s, %s" % (self.title[:20], self.target)

    def get_content(self):
        """get article content."""
        resp = sess.get(self.target)
        cont = etree.HTML(resp.content).xpath(api.x_post_content)
        self.full_text = "\n".join(cont)

    def get_comments(self, page: int = 1, count: int = 20, asc: str = 'false'):
        """get article comments.

        :param page: (optional) page number, default is `1`.
        :param count: (optional) the number of results, default is `20`.
        :param asc: (optional) ascending order, default is `false`.
        """
        resp = sess.get(api.comments % (self.id, count, page, asc))
        dt = resp.ok and resp.json()
        self.comments = {
            'count': dt['count'],
            'page': dt['page'],
            'maxpage': dt['maxPage'],
            'list': [Comment(i, self) for i in dt['comments']]
        }

    def _set_like(self, apiurl: str = api.post_like):
        """like or unlike the article."""
        data = {'id': self.id}
        dt = sess.post(apiurl, data=data).json()
        return dt.get('success') or False

    def like(self):
        """like the article. (require login)"""
        return self._set_like(api.post_like)

    def unlike(self):
        """unlike the article. (require login)"""
        return self._set_like(api.post_unlike)

    def favorite(self):
        """favorite the article. (require login)"""
        dt = sess.get(api.post_favorite % self.id).json()
        return dt.get('favorited')

    def unfavorite(self):
        """unfavorite the article. (require login)"""
        dt = sess.get(api.post_unfavorite % self.id).json()
        return dt.get('success') or False


class User:
    # TODO: talk
    """A user-created :class:`User <instance_id>` object.

    :param *args: need a `uid` or user dict.
    """

    def __init__(self, *args):
        uid: int = 0
        dt: dict = {}

        if isinstance(args[0], int):
            uid = args[0]
        elif isinstance(args[0], dict):
            dt = args[0]

        if uid:
            resp = sess.get(api.user_page % uid)
            self._resp = resp
            dt = resp.ok and resp.json()['user']

        self.logined = False
        self.id = dt['id']
        self.profile = f"{api.prefix}/u/{self.id}"
        self.name = clean_html(dt.get('screen_name') or f"用户{self.id}")
        self.city = (dt.get('province') or "") + (dt.get('city') or "")
        self.description = dt.get('description')
        self.friends_count = dt.get('friends_count')     # 关注数
        self.followers_count = dt.get('followers_count') # 粉丝数
        self.posts_count = dt.get('status_count')        # 帖子数
        self.stocks_count = dt.get('stocks_count')       # 股票数
        self.friends = {}   # 关注
        self.followers = {} # 粉丝
        self.posts = {}     # 帖子
        self.articles = {}  # 专栏
        self.favorites = {} # 收藏
        self.stocks = {}    # 股票
        self.hot_stocks = {}

    def __repr__(self):
        return "<xueqiu.User %s(%s)>" % (self.name, self.id)

    def __str__(self):
        return "%s(%s)" % (self.name, self.id)

    def get_friends(self, page: int = 1):
        """get your friends.

        :param page: (optional) page number, default is `1`.
        """
        resp = sess.get(api.user_friends % (self.id, page))
        dt = resp.ok and resp.json()
        self.friends = {
            'count': self.friends_count, # dt['count']
            'page': dt['page'],
            'maxpage': dt['maxPage'],
            'list': [User(i) for i in dt['users']]
        }

    def get_followers(self, page: int = 1):
        """get your fans.

        :param page: (optional) page number, default is `1`.
        """
        resp = sess.get(api.user_follows % (self.id, page))
        dt = resp.ok and resp.json()
        self.followers = {
            'count': dt['count'],
            'page': dt['page'],
            'maxpage': dt['maxPage'],
            'list': [User(i) for i in dt['followers']]
        }

    def get_posts(self, page: int = 1, count: int = 10):
        """get your posts.

        :param page: (optional) page number, default is `1`.
        :param count: (optional) the number of results, default is `10`.
        """
        resp = sess.get(api.user_post % (self.id, page, count))
        dt = resp.ok and resp.json()
        self.posts = {
            'count': dt['total'],
            'page': dt['page'],
            'maxpage': dt['maxPage'],
            'list': [Post(i) for i in dt['statuses']]
        }

    def get_articles(self, page: int = 1, count: int = 10):
        """get your articles.

        :param page: (optional) page number, default is `1`.
        :param count: (optional) the number of results, default is `10`.
        """
        resp = sess.get(api.user_article % (self.id, page, count))
        dt = resp.ok and resp.json()
        self.articles = {
            'count': dt['total'],
            'page': dt['page'],
            'maxpage': dt['maxPage'],
            'list': [Post(i) for i in dt['list']]
        }

    def get_favorites(self, page: int = 1, count: int = 20):
        """get your favorite posts.

        :param page: (optional) page number, default is `1`.
        :param count: (optional) the number of results, default is `20`.
        """
        resp = sess.get(api.user_favorite % (self.id, page, count))
        dt = resp.ok and resp.json()
        self.favorites = {
            'count': dt['count'],
            'page': dt['page'],
            'maxpage': dt['maxPage'],
            'list': [Post(i) for i in dt['list']]
        }

    def get_stocks(self, mkt: int = 1, count: int = 1000):
        """get your stocks.

        :param mkt: (optional) market type, default is `1`.
                    value: 全球1, 沪深5, 港股7, 美股6
        :param count: (optional) the number of results, default is `1000`.
        """
        # user_stocks: exchange, name, symbol
        resp = sess.get(api.user_stocks % (self.id, mkt, count))
        dt = resp.ok and resp.json()['data']
        resp = sess.get(api.stocks_quote_v5 % ",".join(
            [i['symbol'] for i in dt['stocks']]))
        dt = resp.ok and resp.json()['data']
        mkt_tpe = {
            '1': 'all',
            '5': 'sh',
            '7': 'hk',
            '6': 'us',
        }
        self.stocks = {
            'market': mkt_tpe[f"{mkt}"],
            'count': len(dt['items']),
            'list': [Stock(i['quote']) for i in dt['items']]
        }

    def get_hot_stocks(self, mkt: int = 10, time_range: str = "hour", count: int = 10):
        """get hottest stocks.

        :param mkt: (optional) market type, default is `10`.
                    value: 全球10 沪深12 港股13 美股11
        :param time_range: (optional) hottest stocks by time range, default is `hour`.
                    value: hour, day
        :param count: (optional) the number of results, default is `10`.
        """
        ht = {'hour': 0, 'day': 10}
        resp = sess.get(api.hot_stocks % (mkt+ht[time_range], count))
        dt = resp.ok and resp.json()['data']
        mkt_tpe = {
            '10': 'all',
            '12': 'sh',
            '13': 'hk',
            '11': 'us',
        }
        self.hot_stocks = {
            'market': mkt_tpe[f"{mkt}"],
            'time_range': time_range,
            'list': [Stock(i['code']) for i in dt['items']]
        }

    @staticmethod
    def send_verification_code(phone: int):
        """send verification code to your phone.

        :param phone: your phone number.
        note: only 5 times a day.
        """
        data = {'areacode': 86, 'telephone': phone}
        sess.post(api.send_code, data=data)

    def login(self, uid: str = '', passwd: str = '', login_type: str = 'phone'):
        """user login by password or verification code.

        If the cookie cache exists, load it first and return.
        Otherwise, login and save the cookie to file.

        :param uid: your username or phone number.
        :param passwd: your password or verification code.
        :param login_type: (optional) login type, default is `phone`.
                    value: password, phone
        """
        if self.logined: return self.logined
        elif self.load_cookie(): return self.logined  # load cookie

        # user login
        data = {'phone':    {'remember_me':'true', 'areacode':86,  'telephone':uid, 'code':passwd},
                'password': {'remember_me':'true', 'username':uid, 'password':passwd}}
        resp = sess.post(api.user_login, data=data[login_type])
        self._resp_login = resp  # for debug
        dt = resp.ok and resp.json()
        self.logined = dt.get('login_success') or False
        assert 'error_code' not in dt.keys(), dt.get("error_description")  # login fails

        # save cookie
        if os.path.exists(os.path.dirname(api.cookie_file)):
            sess.cookies.save(ignore_discard=True, ignore_expires=True)
        return self.logined

    def load_cookie(self):
        """load cookies from file or browser."""
        cookies = [i for i in browsercookie.load() if i.domain.find("xueqiu")>0]
        # load cookies from file
        if os.path.exists(api.cookie_file):
            sess.cookies.load(ignore_discard=True, ignore_expires=True)
            self.logined = True
        # load cookies from browser
        elif cookies and 'xq_is_login' in [i.name for i in cookies]:
            [sess.cookies.set_cookie(ck) for ck in cookies]
            self.logined = True
        return self.logined


class Selector:
    # 组装queries, 检查key, 解析url， 返回list
    # TODO: check key, return obj
    """A stock selector :class:`Selector <instance_id>` object.

    :param market: market string, default is `SH`.
                vaule: SH, HK, US
    """

    def __init__(self, market: str = 'SH'):
        self.market = market  # SH, HK, US
        self._industries = self._get(api.select_industries % self.market)  # 行业
        self._areas = self._get(api.select_areas)  # 地区
        self._fields = self._get(api.select_fields % self.market)  # 指标
        self._params = None  # for check
        self.queries = dict(
            category = market,
            exchange = '',  # SH, SZ
            indcode = '',   # 行业
            areacode = '',  # 地区
            orderby = 'symbol',
            order = 'desc',
            current = 'ALL',
            pct = 'ALL',
            page = 1,
            size = 10,
        )
        self.help(show='init_check')
        self._resp = {}  # for debug

    def __repr__(self):
        return "<xueqiu.Selector %s>" % (self.url())

    def __str__(self):
        return "%s" % (self.url())

    def _get(self, *args, **kwargs):
        resp = sess.get(*args, **kwargs)
        self._resp = resp
        dt = resp.ok and resp.json()
        return dt

    def run(self):
        """sends a stock screener request."""
        dt = self._resp and self._resp.url == self.url() and self._resp.json() or \
                self._get(api.selector, params=self.queries)
        return {'count': dt['count'],
                'list': [Stock(i) for i in dt['list']]}

    def url(self):
        """return a selector url string."""
        return api.selector +'?'+ urlencode(self.queries)

    def help(self, range: str = "base", show: str = "text"):
        """show selector parameters.

        :param range: (optional) parameters range, default is `base`.
            value:
                SH: industries, areas, base, ball, quota, finan_rate, stock_data,
                   profit_sheet, balance_sheet, cash_sheet
                HK: industries, base, ball, quota
                US: industries, base, ball, quota, grow,
                   profit_sheet, balance_sheet, cash_sheet
        :param show: (optional) output help or return generator, default is `text`.
            value: text, keys
        """
        select = dict(
            base = [self._fields['基本指标'], ('field', 'name')],
            ball = [self._fields['雪球指标'], ('field', 'name')],
            quota = [self._fields['行情指标'], ('field', 'name')])
        if self.market in ["SH", "US"]:
            select.update(
                profit_sheet = [self._fields['财务报表'][-3]['利润表'], ('field', 'name')],
                balance_sheet = [self._fields['财务报表'][-2]['资产负债表'], ('field', 'name')],
                cash_sheet = [self._fields['财务报表'][-1]['现金流量表'], ('field', 'name')])
        if self.market in ["HK", "US"]:
            select.update(industries = [self._industries['list'], ('plate', 'plate')])
        if self.market == "SH":
            select.update(
                industries = [self._industries['list'], ('level2code', 'level2name')],
                areas = [self._areas['list'], ('keycode', 'keyname')],
                finan_rate = [self._fields['财务比率'], ('field', 'name')],
                stock_data = [self._fields['财务报表'][0]['每股数据'], ('field', 'name')])
        elif self.market == "US":
            select.update(grow = [self._fields['成长指标'], ('field', 'name')])

        # params check
        if not self._params:
            _sele = select.copy()
            _sele.pop('industries') and 'areas' in _sele.keys() and _sele.pop('areas')
            self._params = [j[i[1][0]] for i in _sele.values() for j in i[0]]  # for check
            self._params.append('symbol')

        k = select[range][1]
        if show == 'text':
            for i in select[range][0]:
                adj = i.get("adj") and "[.t]" or ""
                field = i.get(k[0])+adj
                comment = i.get("comment") or ""
                print("{field:<15s}{name:<20s}{comment}".format(
                    field=field, name=i.get(k[1]), comment=comment))
        elif show == 'keys':
            return (i.get(k[0]) for i in select[range][0])  # for cheak

    def scope(self, exchange: str = '', indcode: str = '', areacode: str = ''):
        """set stock selector scope.

        :param exchange: (optional) set a-share exchange market, default is `None`.
                    vaule: SH, SZ or None
        :param indcode: (optional) set industry code, default is `None`.
                    vaule: please see `self.help('industries')`
        :param areacode: (optional) set area code, default is `None`.
                    value: please see `self.help('areas')`
        """
        exchange = exchange in ['SH', 'SZ', ''] and exchange or self.queries['exchange']
        indcode = indcode in self.help('industries', show='keys') and indcode or self.queries['indcode']
        areacode = areacode in self.help('areas', show='keys') and areacode or self.queries['areacode']
        self.queries.update(exchange=exchange, indcode=indcode, areacode=areacode)
        return self

    def param(self, *args, **kwargs):
        """set stock selector paramters.

        :param *args: (optional) set parameters key, default value is `ALL`.
                for example, the `self.param('pb', 'mc')` will be set `pb=ALL&mc=ALL` params.
        :param **kwargs: (optional) set parameters key and value.
                for example, the `self.param('pettm'=0_30)` will be set `pettm=0_30` param.

        Usage::

          >>> import xueqiu
          >>> sel = xueqiu.Selector()
          >>> sel.param(roediluted.20180331=0_100,
                        eps.20180630=0_12,
                        netprofit.20180930=0_23962,
                        bps.20181231=ALL)
          >>> sel.url()
        """
        # check args
        for i in args:
            if i.split('_')[0] in self._params:
                self.queries.update({i.replace('_','.'): "ALL"})
        # check kwargs
        keys = [i.split('_')[0] for i in kwargs.keys()]
        for k in keys:
            k not in self._params and kwargs.pop(k)
        for k,v in kwargs.items():
            self.queries.update({k.replace('_','.'): v})
        return self

    def orderby(self, key: str = 'symbol'):
        """stock selector results are sorted by field.

        :param key: the results are sorted by the `key`, default is `symbol`.
                    the key parameters can be viewed through `self.help('base')`.
        """
        key = key in self._params and key or self.queries['orderby']
        self.queries.update(orderby=key)
        return self

    def order(self, ord: str = 'desc'):
        """set stock selector results are sorted.

        :param ord: the ascending and descending order, default is `desc`.
                    value: asc, desc
        """
        ord = ord in ['desc', 'asc'] and ord or self.queries['order']
        self.queries.update(order=ord)
        return self

    def page(self, page: int = 1):
        """set stock selector results page number.

        :param page: the page number, default is `1`.
        """
        page = isinstance(page, int) and page>0 and page or self.queries['page']
        self.queries.update(page=page)
        return self

    def count(self, size: int = 10):
        """the number of stock selector results.

        :param size: the number of results per page, default is `10`.
        """
        size = isinstance(size, int) and size>0 and size or self.queries['size']
        self.queries.update(size=size)
        return self


class Stock:
    """Stock class"""

    def __init__(self, code: str):
        if isinstance(code, dict):
            code = code.get("symbol") or code.get("code")

        stock_api = api.stocks_quote_v4 if code[0] == "F" else api.stock_quote
        resp = sess.get(stock_api % check_symbol(code))
        self._resp = resp  # for debug
        if resp.ok:
            dt = resp.json()[code] if code[0] == "F" else resp.json()['data']['quote']

        # base (stock_quotec_v5, stock_quote, stocks_quote_v5)
        self.symbol = dt.get('symbol')
        self.code = dt.get('code')  # api.stock_quote
        self.name = dt.get('name')  # api.stock_quote
        self.current = dt.get('current')                                # 当前
        self.current_year_percent = dt.get('current_year_percent')      # 年至今回报
        self.percent = dt.get('percent') and \
            round(float(dt.get('percent'))/100,4) or 0                  # 涨跌幅
        self.chg = dt.get('chg')                                        # 涨跌额
        self.open = dt.get('open')                                      # 今开
        self.last_close = dt.get('last_close')                          # 昨收
        self.high = dt.get('high')                                      # 最高
        self.low = dt.get('low')                                        # 最低
        self.avg_price = dt.get('avg_price')                            # 均价
        self.volume = dt.get('volume')                                  # 成交量
        self.amount = dt.get('amount')                                  # 成交额
        self.turnover_rate = dt.get('turnover_rate')                    # 换手
        self.amplitude = dt.get('amplitude')                            # 振幅
        self.market_capital = dt.get('market_capital')                  # 总市值
        self.float_market_capital = dt.get('float_market_capital')      # 流通市值
        # base (stock_quote, stocks_quote_v5)
        self.total_shares = dt.get('total_shares')                      # 总股本
        self.float_shares = dt.get('float_shares')                      # 流通股
        self.currency = dt.get('currency')                              # 货币单位
        self.exchange = dt.get('exchange')                              # 交易所
        self.issue_date = dt.get('issue_date') and \
            arrow.get(dt.get('issue_date')/1000) or 0                   # 上市日期
        # extend (stock_quote)
        self.limit_up = dt.get('limit_up')                              # 涨停
        self.limit_down = dt.get('limit_down')                          # 跌停
        self.high52w = dt.get('high52w')                                # 52周最高
        self.low52w = dt.get('low52w')                                  # 52周最低
        self.volume_ratio = dt.get('volume_ratio')                      # 量比
        #self.pankou_ratio = resp['data']['others']['pankou_ratio']      # 委比
        self.pe_lyr = dt.get('pe_lyr')                                  # pe静
        self.pe_ttm = dt.get('pe_ttm')                                  # pe滚动
        self.pe_forecast = dt.get('pe_forecast')                        # pe动
        self.pb = dt.get('pb')                                          # pb
        self.eps = dt.get('eps')                                        # 每股收益
        self.bps = dt.get('navps')                                      # 每股净资产
        self.dividend = dt.get('dividend')                              # 股息
        self.dividend_yield = dt.get('dividend_yield')                  # 股息率
        self.profit = dt.get('profit')                                  # 净利润
        self.profit_forecast = dt.get('profit_forecast')                # 净利润(预测)
        self.profit_four = dt.get('profit_four')                        # 净利润(滚动)
        # others
        self.time = arrow.get(dt.get('timestamp')/1000)
        self.posts = {}      # 股票帖子
        self.followers = {}  # 股票粉丝
        self.prousers = {}   # 专业用户
        self.popstocks = []  # 粉丝关注股票
        self.industries = {} # 同行业股票
        self.history = {}    # 历史行情
        self.base_indicator_yahoo = get_quote_yahoo(self.symbol)  # 基本指标(雅虎)
        self.base_indicator = self.indicator()  # 基本指标

    def __repr__(self):
        return "<xueqiu.Stock %s[%s]>" % (self.name, self.symbol)

    def __str__(self):
        return "%s[%s]" % (self.name, self.symbol)

    def _str2date(self, s: str):
        date = lambda **kw: arrow.now().replace(**kw)
        n, k = s[:-1], s[-1]
        bg = {'d':['days',n],
              'w':['weeks',n],
              'm':['months',n],
              'y':['years',n],
              'c':{'years':-1, 'month':12, 'day':31}}
        if   s == 'issue': return self.issue_date
        elif s == 'cyear': return date(**bg['c'])
        return date(**{bg[k][0]: int(bg[k][1])})

    def refresh(self, dt: dict = {}):
        """get current stock data."""
        if not dt:
            # get data from network or dict
            resp = sess.get(api.stock_quotec_v5 % self.symbol)
            dt = resp.ok and resp.json()['data'] and resp.json()['data'][0]
        self.current = dt.get('current')                                # 当前
        self.current_year_percent = dt.get('current_year_percent')      # 年至今回报
        self.percent = dt.get('percent')                                # 涨跌幅
        self.chg = dt.get('chg')                                        # 涨跌额
        self.open = dt.get('open')                                      # 今开
        self.last_close = dt.get('last_close')                          # 昨收
        self.high = dt.get('high')                                      # 最高
        self.low = dt.get('low')                                        # 最低
        self.avg_price = dt.get('avg_price')                            # 均价
        self.volume = dt.get('volume')                                  # 成交量
        self.amount = dt.get('amount')                                  # 成交额
        self.turnover_rate = dt.get('turnover_rate')                    # 换手
        self.amplitude = dt.get('amplitude')                            # 振幅
        self.market_capital = dt.get('market_capital')                  # 总市值
        self.float_market_capital = dt.get('float_market_capital')      # 流通市值
        self.time = arrow.now()

    def get_posts(self, page: int = 1, count: int = 20,
                  sort: str = "time", source: str = "all"):
        """get stock posts.

        :param page: (optional) page number, default is `1`.
        :param count: (optional) the number of results, default is `20`.
        :param sort: (optional) order type, default is `time`.
                    value: time最新, reply评论, relevance默认
        :param source: (optional) source of the results, default is `all`.
                    value: all, user讨论, news新闻, notice公告, trans交易
        """
        self.posts = search(symbol=self.symbol, query_type="post", page=page,
                            count=count, sort=sort, source=source)

    def get_followers(self, page: int = 1, count: int = 15):
        """get stock fans.

        :param page: (optional) page number, default is `1`.
        :param count: (optional) the number of results, default is `15`.
        """
        resp = sess.get(api.stock_follows % (self.symbol, page, count))
        dt = resp.ok and resp.json()
        self.followers = {
            'count': dt['count'],
            'page': dt['page'],
            'maxpage': dt['maxPage'],
            'list': [User(i) for i in dt['followers']]
        }

    def get_prousers(self, count: int = 5):
        """get stock professional users.

        :param count: (optional) the number of results, default is `5`.
        """
        resp = sess.get(api.pro_users % (self.symbol, count))
        dt = resp.ok and resp.json()
        self.prousers = [User(i) for i in dt]

    def get_popstocks(self, count: int = 8):
        """get pop stocks.

        :param count: (optional) the number of results, default is `8`.
        """
        resp = sess.get(api.stock_popstocks % (self.symbol, count))
        dt = resp.ok and resp.json()
        self.popstocks = [Stock(i) for i in dt]

    def get_industry_stocks(self, count: int = 8):
        """get industry stocks.

        :param count: (optional) the number of results, default is `8`.
        """
        resp = sess.get(api.stock_industry % (self.symbol, count))
        dt = resp.ok and resp.json()
        self.industries = {
            'industryname': dt['industryname'],
            'list': [Stock(i) for i in dt['industrystocks']]
        }

    def get_histories(self, begin: str = '-1m', end: str = arrow.now(),
                      period: str = 'day', indicator: str = 'kline,ma,pe,pb,ps,pcf,market_capital'):
        """get stock history data.

        :param begin: the start date of the results.
                value: -1w -2w -1m -3m -6m -1y -2y -3y -5y cyear issue or YYYY-MM-DD
        :param end: (optional) the end date of the results, default is `now`.
        :param period: (optional) set date period, default is `day`.
                value: day week month quarter year 120m 60m 30m 15m 5m 1m
        :param indicator: (optional) set stock indicator, default is `kline,ma,pe,pb,ps,pcf,market_capital`.
                value: kline,ma,macd,kdj,boll,rsi,wr,bias,cci,psy,pe,pb,ps,pcf,market_capital
        """
        begin = len(begin)>5 and arrow.get(begin,tzinfo="Asia/Shanghai").timestamp \
                             or  self._str2date(begin).timestamp
        end = arrow.get(end).timestamp
        resp = sess.get(api.stock_history % (self.symbol, begin, end, period, indicator))
        dt = resp.ok and resp.json()
        df = pd.DataFrame(
            [[arrow.get(i[0]/1000).to('UTF-8').date()]+i[1:]
                for i in dt['data']['item']],
            columns=['date']+dt['data']['column'][1:])
        self.history = df.set_index('date')

    def _get_sheet(self, sheet_type: str = 'cash_flow', quarter: str = 'all', count: int = 12, lang: str = 'cn'):
        sht = {'income': [api.income, sheet.income_lang],
               'balance': [api.balance, sheet.balance_lang],
               'cash_flow': [api.cash_flow, sheet.cash_flow_lang],
               'indicator': [api.indicator, sheet.indicator_lang]}
        reg = {'SH':'cn', 'SZ':'cn', 'HK':'hk', 'NYSE':'us'}
        region = reg[self.exchange]
        resp = sess.get(sht[sheet_type][0] % (region, self.symbol, quarter, count))
        dt = json.loads(resp.text.replace('一季报','Q1').replace('中报','Q2').replace('三季报','Q3').replace('年报','Q4'))
        df = pd.DataFrame([{j: i[j][0] if isinstance(i[j], list) else i[j]
            for j in i} for i in dt['data']['list']]).set_index('report_name')
        if lang == 'cn':
            df = df.rename(columns=sht[sheet_type][1][region])
        return df

    def indicator(self, quarter: str = 'last', count: int = 12, lang: str = 'cn'):
        """get stock indicator.

        :param quarter: (optional) sheet type, default is `last`.
            value: S0(single quarter) Q1-Q4 all last.
        :param count: (optional) the number of results, default is `12`.
        :param lang: (optional) sheet language, default is `cn`.
        """
        if quarter == 'last' or self.exchange == 'HK':
            reg = {'SH':'cn', 'SZ':'cn', 'HK':'hk', 'NYSE':'us'}
            region = reg[self.exchange]
            columns = sheet.f10_indicator_ks['base'].copy()
            columns.update(sheet.f10_indicator_ks[region])
            resp = sess.get(api.f10_indicator % (region, self.symbol))
            df = pd.DataFrame(resp.json()['data']['items'])
            return df.rename(columns=columns)
        return self._get_sheet('indicator', quarter.upper(), count)

    def income(self, quarter: str = 'all', count: int = 12, lang: str = 'cn'):
        """get stock income sheet.

        :param quarter: (optional) sheet type, default is `all`.
            value: S0(single quarter) Q1-Q4 all.
        :param count: (optional) the number of results, default is `12`.
        :param lang: (optional) sheet language, default is `cn`.
        """
        return self._get_sheet('income', quarter.upper(), count)

    def balance(self, quarter: str = 'all', count: int = 12, lang: str = 'cn'):
        """get stock balance sheet.

        :param quarter: (optional) sheet type, default is `all`.
            value: S0(single quarter) Q1-Q4 all.
        :param count: (optional) the number of results, default is `12`.
        :param lang: (optional) sheet language, default is `cn`.
        """
        return self._get_sheet('balance', quarter.upper(), count)

    def cash_flow(self, quarter: str = 'all', count: int = 12, lang: str = 'cn'):
        """get stock cash flow sheet.

        :param quarter: (optional) sheet type, default is `all`.
            value: S0(single quarter) Q1-Q4 all.
        :param count: (optional) the number of results, default is `12`.
        :param lang: (optional) sheet language, default is `cn`.
        """
        return self._get_sheet('cash_flow', quarter.upper(), count)


class Fund(Stock):
    """Fund class"""

    def __init__(self, code: str, stocks: list = []):
        Stock.__init__(self, check_symbol(code))
        self.fund_nav = self.get_fund_nav()  # 净值 涨跌幅
        self.fund_nav_guess = 0  # 估值 涨跌幅
        self.fund_nav_premium = 0  # 溢价率
        self.fund_history = {}   # 历史净值
        self.fund_stocks = stocks and pd.DataFrame({
            'stocks': create_or_refresh_stocks(stocks[0]),
            'weight': stocks[1]})  # 成份股 权重

    def __repr__(self):
        return "<xueqiu.Fund %s[%s]>" % (self.name, self.symbol)

    def get_fund_stocks(self, year: str = "", mouth: str = "12"):
        """get fund stocks."""
        # TODO 选季报
        resp = sess.get(api.fund_stocks % (self.code, year, mouth))
        stock = [re.findall(api.x_fund_stocks, i)
                    for i in re.split("截止至", resp.text)[1:]]
        self.fund_stocks = pd.DataFrame({
            'stocks': create_or_refresh_stocks([i[0] for i in stock[0]]),
            'weight': [round(float(i[2])/100,4) for i in stock[0]]})

    def get_fund_nav(self):
        """get fund nav."""
        resp = sess.get(api.fund_nav % self.code)
        nav = etree.HTML(resp.text).xpath(api.x_fund_nav)[:-2]
        nav[1], nav[2] = float(nav[1]), float(nav[2])
        return nav

    def get_fund_histories(self, begin: str = '-1m', end: str = arrow.now(), size: int = 1024):
        """get fund history data.

        :param begin: the start date of the results.
                value: -1w -2w -1m -3m -6m -1y -2y -3y -5y cyear issue or YYYY-MM-DD
        :param end: (optional) the end date of the results, default is `now`.
        :param size: (optional) the number of results, default is `1024`.
        """
        begin = len(begin)>5 and arrow.get(begin).format('YYYY-MM-DD') \
                             or  self._str2date(begin).format('YYYY-MM-DD')
        end = arrow.get(end).format('YYYY-MM-DD')
        resp = sess.get(api.fund_history % (self.code, begin, end, size))
        df = pd.DataFrame(
                re.findall(api.x_fund_history, resp.text),
                columns=['date','nav','cnav','percent'])
        df['date'] = pd.to_datetime(df['date'])
        self.fund_history = df.set_index('date').sort_index(axis=0)

    def calc_premium(self):
        """calculate fund premium."""
        # exchange rate
        #usd, hkd = exusd(), exhkd()
        #ex = {'USD': usd[0]/usd[1], 'HKD': hkd[0]/hkd[1]}
        #exrate = np.array([ex[i.currency] for i in self.fund_stocks])
        percent = np.array([i.percent for i in self.fund_stocks.stocks])
        weight = np.array(self.fund_stocks.weight)
        # 当前/(净值*1+sum(涨跌幅*权重*汇率))-1
        fund_percent = sum(percent*weight)/sum(weight)
        self.fund_nav_guess = round(self.fund_nav[1]*(1+fund_percent),4), round(fund_percent,6),
        self.fund_nav_premium = round(self.current/self.fund_nav_guess[0]-1, 6)

    def refresh_all(self):
        """refresh all of the fund stock objects."""
        create_or_refresh_stocks([self] + [i for i in self.fund_stocks])