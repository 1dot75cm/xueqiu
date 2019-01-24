# -*- coding: utf-8 -*-

"""
xueqiu.model
~~~~~~~~~~~~

This module implements a humanize XueQiu API wrappers.

:copyright: (c) 2019 by 1dot75cm.
:license: MIT, see LICENSE for more details.
"""

__all__ = ['news', 'search', 'Selector', 'Stock', 'Post', 'User']

from .utils import clean_html
from .utils import sess
from . import api
from lxml import etree
from urllib.parse import urlencode
import arrow
import json
import os


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
                value: 头条-1, 直播6, 沪深105, 港股102, 美股101,
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


class Comment:
    """A user-created :class:`Comment <instance_id>` object.

    :param dt: the dictionary contains comment data.
    """

    def __init__(self, dt: dict):
        self.id = dt['id']
        self.user = User(dt['user'])
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
        header = {'X-Requested-With': 'XMLHttpRequest'}  # ajax request
        resp = sess.post(apiurl, headers=header, data=data)
        dt = resp.ok and resp.json()
        return dt.get('success')

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
        self.id = dt['id']
        self.user = User(dt.get('user') or dt.get('user_id'))
        self.created_at = arrow.get(dt['created_at']/1000)
        self.target = api.prefix + dt['target']  # 文章url
        self.view_count = dt.get('view_count')  # 访问量
        self.talk_count = dt.get('talk_count')  # 评论数
        self.like_count = dt.get('like_count')  # 点赞数
        self.title = dt.get('title')
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
            'list': [Comment(i) for i in dt['comments']]
        }

    def _set_like(self, apiurl: str = api.post_like):
        """like or unlike the article."""
        data = {'id': self.id}
        header = {'X-Requested-With': 'XMLHttpRequest'}  # ajax request
        resp = sess.post(apiurl, headers=header, data=data)
        dt = resp.ok and resp.json()
        return dt.get('success')

    def like(self):
        """like the article. (require login)"""
        return self._set_like(api.post_like)

    def unlike(self):
        """unlike the article. (require login)"""
        return self._set_like(api.post_unlike)

    def favorite(self):
        """favorite the article. (require login)"""
        resp = sess.get(api.post_favorite % self.id)
        dt = resp.ok and resp.json()
        return dt.get('favorited')

    def unfavorite(self):
        """unfavorite the article. (require login)"""
        resp = sess.get(api.post_unfavorite % self.id)
        dt = resp.ok and resp.json()
        return dt.get('success')


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

    def get_stocks(self, mkt: int = 1, count: int = 1000):
        """get your stocks.

        :param mkt: (optional) market type, default is `1`.
                    value: 全球1, 沪深5, 港股7, 美股6
        :param count: (optional) the number of results, default is `1000`.
        """
        resp = sess.get(api.user_stocks % (self.id, mkt, count))
        dt = resp.ok and resp.json()['data']
        mkt_tpe = {
            '1': 'all',
            '5': 'sh',
            '7': 'hk',
            '6': 'us',
        }
        self.stocks = {
            'market': mkt_tpe[f"{mkt}"],
            'count': len(dt['stocks']),
            'list': [Stock(i) for i in dt['stocks']]
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
        # load cookie cache
        elif os.path.exists(api.cookie_file):
            self.logined = True
            sess.cookies.load(ignore_discard=True, ignore_expires=True)
            return self.logined

        # user login
        data = {'phone':    {'remember_me':'true', 'areacode':86,  'telephone':uid, 'code':passwd},
                'password': {'remember_me':'true', 'username':uid, 'password':passwd}}
        header = {'X-Requested-With': 'XMLHttpRequest'}  # ajax request
        resp = sess.post(api.user_login, headers=header, data=data[login_type])
        self._resp_login = resp  # for debug
        dt = resp.ok and resp.json()
        self.logined = dt.get('login_success') or False
        assert 'error_code' not in dt.keys(), dt.get("error_description")  # login fails

        # save cookie
        if os.path.exists(os.path.dirname(api.cookie_file)):
            sess.cookies.save(ignore_discard=True, ignore_expires=True)
        return self.logined


def stocks():
    # TODO: 行情
    pass

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

    def __repr__(self):
        return "<xueqiu.Selector %s>" % (self.url())

    def __str__(self):
        return "%s" % (self.url())

    @staticmethod
    def _get(*args, **kwargs):
        resp = sess.get(*args, **kwargs)
        dt = resp.ok and resp.json()
        return dt

    def run(self):
        """sends a stock screener request."""
        return self._get(api.selector, params=self.queries)

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
            if i.split('.')[0] in self._params:
                self.queries.update({i: "ALL"})
        # check kwargs
        keys = [i.split('.')[0] for i in kwargs.keys()]
        for k in keys:
            k not in self._params and kwargs.pop(k)
        self.queries.update(kwargs)
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
            code = code.get("code") or code.get("symbol")

        stock_api = api.stocks_quote_v4 if code[0] == "F" else api.stock_quote
        resp = sess.get(stock_api % code)
        self._resp = resp
        if resp.ok:
            dt = resp.json()[code] if code[0] == "F" else resp.json()['data']['quote']

        self.symbol = dt.get('symbol')
        self.code = dt.get('code')
        self.name = dt.get('name')
        self.current = dt.get('current')                                # 当前
        self.percent = dt.get('percent')                                # 涨跌幅
        self.chg = dt.get('chg')                                        # 涨跌额
        self.open = dt.get('open')                                      # 今开
        self.last_close = dt.get('last_close')                          # 昨收
        self.high = dt.get('high')                                      # 最高
        self.low = dt.get('low')                                        # 最低
        self.avg_price = dt.get('avg_price')                            # 均价
        self.limit_up = dt.get('limit_up')                              # 涨停
        self.limit_down = dt.get('limit_down')                          # 跌停
        self.volume = dt.get('volume')                                  # 成交量
        self.amount = dt.get('amount')                                  # 成交额
        self.volume_ratio = dt.get('volume_ratio')                      # 量比
        #self.pankou_ratio = resp['data']['others']['pankou_ratio']    # 委比
        self.turnover_rate = dt.get('turnover_rate')                    # 换手
        self.amplitude = dt.get('amplitude')                            # 振幅
        self.pe_lyr = dt.get('pe_lyr')                                  # pe静
        self.pe_ttm = dt.get('pe_ttm')                                  # pe滚动
        self.pe_forecast = dt.get('pe_forecast')                        # pe动
        self.pb = dt.get('pb')                                          # pb
        self.eps = dt.get('eps')                                        # eps
        self.bps = dt.get('navps')                                      # navps
        self.dividend_yield = dt.get('dividend_yield')                  # 股息率
        self.total_shares = dt.get('total_shares')                      # 总股本
        self.float_shares = dt.get('float_shares')                      # 流通股
        self.market_capital = dt.get('market_capital')                  # 总市值
        self.float_market_capital = dt.get('float_market_capital')      # 流通市值
        self.high52w = dt.get('high52w')                                # 52周最高
        self.low52w = dt.get('low52w')                                  # 52周最低
        self.currency = dt.get('currency')                              # 货币单位
        self.exchange = dt.get('exchange')                              # 交易所
        #self.time = arrow.get(dt.get('time')/1000)
        self.posts = {}  # 股票相关帖子

    def __repr__(self):
        return "<xueqiu.Stock %s[%s]>" % (self.name, self.symbol)

    def __str__(self):
        return "%s[%s]" % (self.name, self.symbol)

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
