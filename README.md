# xueqiu
a humanize XueQiu API wrappers.

## Quick start

Installation

```sh
pip install xueqiu
```

Example:

```python
>>> news = xueqiu.news()  # watch the news
>>> news
{'list': [<xueqiu.Post 为何价值投资长期有效[https://xueqiu.com/8291461932/120351059]>,
  <xueqiu.Post 韬蕴资本CEO温晓东怒斥贾跃亭：怎就一个[https://xueqiu.com/2095268812/120483699]>,
  <xueqiu.Post 增持与回购20190122-201901[https://xueqiu.com/9206540776/120458648]>,
  <xueqiu.Post 医药研发外包为什么这么红?(上)[https://xueqiu.com/1472391509/120481662]>,
  <xueqiu.Post 医药大赛道之大分子生物药（下）[https://xueqiu.com/1472391509/120482094]>,
  <xueqiu.Post 增强型指数基金，到底“强”在哪里？[https://xueqiu.com/8082119199/120480761]>,
  <xueqiu.Post 价值投资不需要概率思维吗？—与董宝珍先生[https://xueqiu.com/3555476733/120245234]>,
  <xueqiu.Post 邓晓峰的投资观[https://xueqiu.com/7649503965/120430145]>,
  <xueqiu.Post 复利无敌：买入一只股票看这四点[https://xueqiu.com/1876906471/120479202]>,
  <xueqiu.Post 再论安全边际[https://xueqiu.com/4465952737/120453192]>],
 'next_max_id': 20323343}
>>> p = news['list'][0]
>>> "{} {} 赞{} 评论{} 转发{} {}".format(p.title, p.user.name, p.like_count,
                                        p.reply_count, p.retweet_count, p.target)
'为何价值投资长期有效 房杨凯的投资世界 赞9 评论11 转发9 https://xueqiu.com/8291461932/120351059'
>>> p.user.get_posts()  # get user's article
>>> p.user.posts
{'count': 622,
 'page': 1,
 'maxpage': 63,
 'list': [<xueqiu.Post [https://xueqiu.com/8291461932/120497097]>,
  <xueqiu.Post [https://xueqiu.com/8291461932/120491351]>,
  <xueqiu.Post [https://xueqiu.com/8291461932/120487476]>,
  <xueqiu.Post [https://xueqiu.com/8291461932/120487448]>,
  <xueqiu.Post [https://xueqiu.com/8291461932/120486037]>,
  <xueqiu.Post 腾讯游戏帝国的护城河还在吗？[https://xueqiu.com/8291461932/120485596]>,
  <xueqiu.Post [https://xueqiu.com/8291461932/120473933]>,
  <xueqiu.Post [https://xueqiu.com/8291461932/120434054]>,
  <xueqiu.Post [https://xueqiu.com/8291461932/120434037]>,
  <xueqiu.Post [https://xueqiu.com/8291461932/120434020]>]}
>>> p.user.posts['list'][0].text  # content
'回复@A8天道酬勤: 这个问题应该放在买之前。//@A8天道酬勤:回复@房杨凯的投资世界:假如花旗银行做假账，聂夫还会不会持有？'
>>> p.user.posts['list'][0].like()  # like this (need login)
```

## API

### User class

A user class that contains user-related methods.

*User object attributes:*

- `id` - user id.
- `profile` - user's profile url.
- `name` - user name.
- `city` - city, for example '上海'.
- `description` - user description.
- `friends_count` - the number of user's friends.
- `followers_count` - the number of user's fans.
- `posts_count` - the number of user's post.
- `stocks_count` - the number of stocks.
- `friends` - use to save `User` object for friends.
- `followers` - use the save `User` object for fans.
- `posts` - use the save `Post` object for post.
- `articles` - use the save `Post` object for user's article.
- `favorites` - use the save `Post` object for favorite articles.
- `stocks` - use the save `Stock` object for favorite stocks.
- `hot_stocks` - use the save `Stock` object for the current hot stocks.

*User object methods:*

- `get_friends(page: int = 1)` - get your friends and save to `self.friends`.
- `get_followers(page: int = 1)` - get your fans and save to `self.followers`.
- `get_posts(page: int = 1, count: int = 10)` - get your posts and save to `self.posts`.
- `get_articles(page: int = 1, count: int = 10)` - get your articles and save to `self.articles`.
- `get_favorites(page: int = 1, count: int = 20)` - get your favorite posts and save to `self.favorites`.
- `get_stocks(mkt: int = 1, count: int = 1000)` - get your stocks and save to `self.stocks`.
- `get_hot_stocks(mkt: int = 10, time_range: str = "hour", count: int = 10)` - get hottest stocks.
    - :param `mkt`: (optional) market type, default is `10`.
        - value: 全球`10` 沪深`12` 港股`13` 美股`11`
    - :param `time_range`: (optional) hottest stocks by time range, default is `hour`.
        - value: `hour`, `day`
    - :param `count`: (optional) the number of results, default is `10`.

- `send_verification_code(phone: int)` - send verification code to your phone. **Note**: only 5 times a day.
- `login(uid: str = '', passwd: str = '', login_type: str = 'phone')` - user login by password or verification code. If the cookie cache exists, load it first and return. Otherwise, login and save the cookie to file (Linux `~/.xueqiu/cookie` or Windows).
    - :param `uid`: your username or phone number.
    - :param `passwd`: your password or verification code.
    - :param `login_type`: (optional) login type, default is `phone`.
        - value: `password`, `phone`

- `load_cookie()` - load cookies from local file or browser(chrome or firefox). You can login your account on the chrome browser, then execute `load_cookie()`, and now login successfully.

Example:
```python
>>> u = User(2478797769)
>>> u.name
"红利基金"
>>> u.get_posts()
>>> u.posts['list'][0].title
'【你了解红利基金吗】红利基金（501029）热问快答！（12.31）'
>>> u.get_favorites()
>>> u.favorites['list'][0].title
'2018年A股大数据盘点：30张图尽览市场热点'
```

### Post class

A post class that contains post-related methods.

*Post object attributes:*

- `id` - post id.
- `user` - post authors. a `User` class object.
- `created_at` - created time. a `Arrow` class object.
- `target` - post url.
- `view_count` - view count.
- `reply_count` - reply count.
- `retweet_count` - retweet count.
- `fav_count` - favorites count.
- `like_count` - like count.
- `title` - post title.
- `text` - post content.
- `full_text` - the full content of the article.
- `comments` - use the save `Comment` object for post.

*Post object methods:*

- `get_content()` - get article content and save to `self.full_text`.
- `get_comments(page: int = 1, count: int = 20, asc: str = 'false')` - get article comments and save to `self.comments`.
- `like()` - like the article. (require login)
- `unlike()` - unlike the article. (require login)
- `favorite()` - favorite the article. (require login)
- `unfavorite()` - unfavorite the article. (require login)

Example:
```python
>>> p = Post('2478797769/78869335')
>>> p.user.name
"红利基金"
>>> p.created_at.format("YYYY-MM-DD")
"2016-12-13"
>>> p.title
'【你了解红利基金吗】红利基金（501029）热问快答！（12.31）'
>>> p.target
"https://xueqiu.com/2478797769/78869335"
>>> p.get_content()
>>> p.full_text
'目录：\n一、\n华宝标普中国A股红利机会指数证券投资基金\n......'
>>> p.get_comments()
>>> p.comments['list'][-1].text
'为什么成份股中有很多次新股？百思不得其解'
```

### Comment class

A comment class that contains comment-related methods.

*Comment object attributes:*

- `id` - comment id.
- `user` - comment authors. a `User` class object.
- `post` - comment on an article. a `Post` class object.
- `created_at` - created time. a `Arrow` class object.
- `like_count` - like count.
- `text` - comment content.

*Comment object methods:*

- `like()` - like the comment. (require login)
- `unlike()` - unlike the comment. (require login)

Example:
```python
>>> p = Post('2478797769/78869335')
>>> p.get_comments()
>>> c = p.comments['list'][0]
>>> c.user.name
'红利基金'
>>> c.text
'回复@孙浩云: 怎么可能....2018年跌幅为24.54%，较主流指数跌幅较小。不知道您50%多是哪儿看来的呢'
```

### Selector class

The `Selector` class implements a stock filter.

*Selector object attributes:*

- `market` - market string, default is `SH`.
    - value: `SH`, `HK`, `US`
- `queries` - include default parameters with selector.

*Selector object methods:*

- `url()` - return a selector url string.
- `help(range: str = "base", show: str = "text")` - show selector parameters.
    - :param `range`: (optional) parameters range, default is `base`.
        value:
        - SH: industries, areas, base, ball, quota, finan_rate, stock_data,
              profit_sheet, balance_sheet, cash_sheet
        - HK: industries, base, ball, quota
        - US: industries, base, ball, quota, grow,
              profit_sheet, balance_sheet, cash_sheet
    - :param `show`: (optional) output help or return generator, default is `text`.
        - value: `text`, `keys`
- `scope(exchange: str = '', indcode: str = '', areacode: str = '')` - set stock selector scope.
    - :param `exchange`: (optional) set A-share exchange market, default is `None`.
        - value: `SH`, `SZ` or `None`
    - :param `indcode`: (optional) set industry code, default is `None`. please see `self.help('industries')`
    - :param `areacode`: (optional) set area code, default is `None`. please see `self.help('areas')`
- `param(*args, **kwargs)` - set stock selector paramters.
    - :param `*args`: (optional) set parameters key, default value is `ALL`.
        for example, the `self.param('pb', 'mc')` will be set `pb=ALL&mc=ALL` params.
    - :param `**kwargs`: (optional) set parameters key and value.
        for example, the `self.param('pettm'=0_30)` will be set `pettm=0_30` param.
- `orderby(key: str = 'symbol')` - stock selector results are sorted by field.
    - :param `key`: the results are sorted by the `key`, default is `symbol`.
            the key parameters can be viewed through `self.help('base')`.
- `order(ord: str = 'desc')` - set stock selector results are sorted.
    - :param `ord`: the ascending and descending order, default is `desc`.
        - value: `asc`, `desc`
- `page(page: int = 1)` - set stock selector results page number.
- `count(size: int = 10)` - the number of stock selector results.
- `run()` - sends a stock screener request and return `[Stock class]` list.

Example:
```python
>>> s = Selector("SH")
# scope 深市，房地产，浙江地区
# param 筛选总市值，18年3季度ROE 0-30%
# orderby 按市值排序
# order 升序排列
# page 第2页
# count 每页2个
>>> result = s.scope('SZ','K70','CN330000').param('mc', roediluted_20180930='0_30').orderby('mc').order('asc').page(2).count(2).run()
>>> result['list']
[<xueqiu.Stock 荣安地产[SZ000517]>, <xueqiu.Stock 滨江集团[SZ002244]>]
```

### Stock class

A stock class that contains stock-related methods.

*Stock object attributes:*

base
- `symbol` - stock symbol.
- `code` - stock code.
- `name` - stock name.
- `current` - current price.
- `current_year_percent` - current year return.
- `percent` - change rate.
- `chg` - change amount.
- `open` - price today.
- `last_close` - last close.
- `high` - highest.
- `low` - lowest.
- `avg_price` - average price.
- `volume` - trading volume.
- `amount` - amount.
- `turnover_rate` - turnover rate.
- `amplitude` - amplitude.
- `market_capital` - market capital.
- `float_market_capital` - float market capital.
- `total_shares` - total shares.
- `float_shares` - float shares.
- `currency` - currency unit.
- `exchange` - stock exchange.
- `issue_date` - launch date. a `Arrow` class object.

extend
- `limit_up` - stock limit up.
- `limit_down` - stock limit down.
- `high52w` - the highest of the fifty-two weeks.
- `low52w` - the lowest of the fifty-two weeks.
- `volume_ratio` - volume ratio.
- `pe_lyr` - pe lyr.
- `pe_ttm` - pe ttm.
- `pe_forecast` - pe forecast.
- `pb` - price/book value ratio.
- `eps` - earnings per share.
- `bps` - net asset value per share.
- `dividend` - stock dividend.
- `dividend_yield` - stock dividend yield.
- `profit` - net profit.
- `profit_forecast` - profit forecast.
- `profit_four` - profit last four quarters.

others
- `time` - current time. a `Arrow` class object.
- `posts` - used to the save `Post` object for stock.
- `followers` - used to the save `User` object for stock's fans.
- `prousers` - used to the save `User` object for stock's professional users.
- `popstocks` - pop stocks.
- `industries` - industry stocks.
- `history` - stock history.

*Stock object methods:*

- `refresh(dt: dict = {})` - get current stock data and update `self.time`.
- `get_posts(page: int = 1, count: int = 20, sort: str = "time", source: str = "all")` - get stock posts and save to `self.posts`.
    - :param `page`: (optional) page number, default is `1`.
    - :param `count`: (optional) the number of results, default is `20`.
    - :param `sort`: (optional) order type, default is `time`.
        - value: `time`最新, `reply`评论, `relevance`默认
    - :param `source`: (optional) source of the results, default is `all`.
        - value: `all`, `user`讨论, `news`新闻, `notice`公告, `trans`交易
- `get_followers(page: int = 1, count: int = 15)` - get stock fans and save to `self.followers`.
    - :param `page`: (optional) page number, default is `1`.
    - :param `count`: (optional) the number of results, default is `15`.
- `get_prousers(count: int = 5)` - get stock professional users and save to `self.prousers`.
- `get_popstocks(count: int = 8)` - get pop stocks and save to `self.popstocks`.
- `get_industry_stocks(count: int = 8)` - get industry stocks and save to `self.industries`.
- `get_histories(begin: str = '-1m', end: str = arrow.now(), period: str = 'day')` - get stock history data and save to `self.history`.
    - :param `begin`: the start date of the results.
        - value: -1w -2w -1m -3m -6m -1y -2y -3y -5y cyear issue or YYYY-MM-DD
    - :param `end`: (optional) the end date of the results, default is `now`.
    - :param `period`: (optional) set date period, default is `day`.
        - value: day week month quarter year 120m 60m 30m 15m 5m 1m

Example:
```python
>>> s = Stock("SH601318")
>>> s.symbol
"SH601318"
>>> s.name
"中国平安"
>>> s.market_capital
1119664786363.0
>>> s.issue_date.format("YYYY-MM-DD")
"2007-02-28"
>>> s.refresh()  # update stock data
>>> s.get_posts()
{'count': 188745,
 'page': 1,
 'maxpage': 100,
 'list': [<xueqiu.Post [https://xueqiu.com/1566609429/120543602]>,
  <xueqiu.Post [https://xueqiu.com/1083048635/120542397]>,
  <xueqiu.Post [https://xueqiu.com/6376335219/120542355]>,
  <xueqiu.Post [https://xueqiu.com/8335420516/120542213]>,
  <xueqiu.Post [https://xueqiu.com/2706248223/120542082]>,
  <xueqiu.Post [https://xueqiu.com/4298761680/120542015]>,
  <xueqiu.Post [https://xueqiu.com/2856403580/120541995]>,
  <xueqiu.Post [https://xueqiu.com/6122867052/120541786]>,
  <xueqiu.Post [https://xueqiu.com/1083048635/120541288]>,
  <xueqiu.Post [https://xueqiu.com/9598902646/120541255]>]}
>>> s.get_popstocks()
>>> s.popstocks
[<xueqiu.Stock 招商银行[SH600036]>,
 <xueqiu.Stock 兴业银行[SH601166]>,
 <xueqiu.Stock 民生银行[SH600016]>,
 <xueqiu.Stock 贵州茅台[SH600519]>,
 <xueqiu.Stock 苏宁易购[SZ002024]>,
 <xueqiu.Stock 万科A[SZ000002]>,
 <xueqiu.Stock 腾讯控股[00700]>,
 <xueqiu.Stock 中绿[02988]>]
>>> s.get_industry_stocks()
>>> s.industries
{'industryname': '非银金融',
 'list': [<xueqiu.Stock 九鼎投资[SH600053]>,
  <xueqiu.Stock 华林证券[SZ002945]>,
  <xueqiu.Stock 爱建集团[SH600643]>,
  <xueqiu.Stock 中航资本[SH600705]>,
  <xueqiu.Stock 华铁科技[SH603300]>,
  <xueqiu.Stock 民生控股[SZ000416]>,
  <xueqiu.Stock 熊猫金控[SH600599]>,
  <xueqiu.Stock 宏源证券[SZ000562]>]}
>>> s.get_histories('2019-01-07','2019-01-11')
>>> s.history
date           volume   open   high    low  close   chg  percent  turnoverrate
2019-01-07   76593007  57.09  57.17  55.90  56.30 -0.29    -0.51          0.70
2019-01-08   55992092  56.05  56.09  55.20  55.80 -0.50    -0.89          0.51
2019-01-09   81914613  56.20  57.60  55.96  56.95  1.15     2.06          0.75
2019-01-10   67328223  56.87  57.82  56.55  57.50  0.55     0.97          0.61
2019-01-11   45756973  58.00  58.29  57.50  58.07  0.57     0.99          0.42
>>> s.get_histories('-1w')
>>> s.history
date           volume   open   high    low  close   chg  percent  turnoverrate
2019-01-24   44940618  59.61  60.52  59.22  60.43  0.94     1.58          0.41
2019-01-25   67245911  60.50  61.78  60.43  61.29  0.86     1.42          0.62
2019-01-28   58164884  61.80  62.41  61.20  61.52  0.23     0.38          0.53
2019-01-29   39519294  61.38  61.90  60.98  61.65  0.13     0.21          0.36
2019-01-30   31000323  60.88  61.86  60.78  61.25 -0.40    -0.65          0.27
```

### Fund class

A fund class that contains fund-related methods.

*Fund object attributes:*

- `fund_nav` - fund net value.
- `fund_nav_guess` - estimate value.
- `fund_nav_premium` - fund nav premium rate.
- `fund_history` - fund history.
- `fund_stocks` - component stocks.
- `fund_weight` - stocks weight.

*Fund object methods:*

- `get_fund_stocks(year: str = "", mouth: str = "12")` - get fund's stocks from `天天基金`.
- `get_fund_nav()` - get fund nav.
- `get_fund_histories(page: int = 1, size: int = 90)` - get history fund nav.
- `calc_premium()` - calculate fund premium.
- `refresh_all()` - refresh all of the fund stock objects.

Example:
```python
>>> f = Fund('501301')
>>> f.symbol
"SH501301"
>>> f.fund_nav
['2019-01-29', 1.1311, 1.1311, '-0.47%']
>>> f.get_fund_stocks()
>>> f.fund_stocks
       stocks          weight
0      中国移动[00941]  0.1082
1      工商银行[01398]  0.0975
2      腾讯控股[00700]  0.0970
3      建设银行[00939]  0.0932
4      中国平安[02318]  0.0922
5      中国银行[03988]  0.0642
6   中国海洋石油[00883]  0.0522
7      中国石化[00386]  0.0343
8      中国人寿[02628]  0.0297
9      招商银行[03968]  0.0267
>>> list(f.fund_stocks.weight)
[0.1082, 0.0975, 0.097, 0.0932, 0.0922, 0.0642, 0.0522, 0.0343, 0.0297, 0.0267]
>>> f.get_fund_histories('2019-01-07','2019-01-11')
>>> f.fund_history
date           nav    cnav percent
2019-01-07  1.0743  1.0743    0.70
2019-01-08  1.0679  1.0679   -0.60
2019-01-09  1.0949  1.0949    2.53
2019-01-10  1.0944  1.0944   -0.05
2019-01-11  1.0964  1.0964    0.18
>>> f.get_fund_histories('-1w')
date           nav    cnav percent
2019-01-25  1.1413  1.1413    2.02
2019-01-28  1.1364  1.1364   -0.43
2019-01-29  1.1311  1.1311   -0.47
2019-01-30  1.1379  1.1379    0.60
2019-01-31  1.1475  1.1475    0.84
```

### search function

- `search(query: str = "", query_type: str = "stock", symbol: str = "", count: int = 10, page: int = 1, sort: str = "time", source: str = "user")` - Sends a search request.
    - :param `query`: query string.
    - :param `query_type`: (optional) type of the query request, default is `stock`.
        - value: stock, post, user
    - :param `symbol`: (optional) the stock symbol.
    - :param `count`: (optional) the number of results, default is `20`.
    - :param `page`: (optional) page number, default is `1`.
    - :param `sort`: (optional) order type, default is `time`.
        - value: time最新, reply评论, relevance默认
    - :param `source`: (optional) source of the results, default is `user`.
        - value: all, user讨论, news新闻, notice公告, trans交易
    - :return: a list of :class:`Object <instance_id>` objects. Object class: Stock, Post or User
    - :rtype: list([ins1, ins2, ...])

### news function

- `news(category: int = -1, count: int = 10, max_id: int = -1)` - Get news.
    - :param `category`: (optional) type of the news, default is `-1`.
        - value: 头条-1, 今日话题0, 直播6, 沪深105, 港股102, 美股101, 基金104, 私募113, 房产111, 汽车114, 保险110
    - :param `count`: (optional) the number of results, default is `10`.
    - :param `max_id`: (optional) the max id of news, default is `-1`.
    - :return: a list of :class:`Post <instance_id>` objects.
    - :rtype: list([post1, post2, ...])

### utils module

This module contains some utils.

- `get_cookies()` - load cookies from local file, browser and selenium. return a `LWPCookieJar` class object.
- `get_session()` - get the requests session.
- `clean_html(tree: str)` - clean html.
- `check_symbol(code: str)` - check stock symbol.
- `exrate(date: str = "", code: str = "USD")` - get the monetary exchange rate by date.
    - code: 
```python
{'USD':'美元','EUR':'欧元','JPY':'日元','HKD':'港元','GBP':'英镑','AUD':'澳大利亚元',
 'NZD':'新西兰元','SGD':'新加坡元','CHF':'瑞士法郎','CAD':'加拿大元','MYR':'马来西亚林吉特',
 'RUB':'俄罗斯卢布','ZAR':'南非兰特','KRW':'韩元','AED':'阿联酋迪拉姆','SAR':'沙特里亚尔',
 'HUF':'匈牙利福林','PLN':'波兰兹罗提','DKK':'丹麦克朗','SEK':'瑞典克朗','NOK':'挪威克朗',
 'TRY':'土耳其里拉','MXN':'墨西哥比索','THB':'泰铢'}
```
- `exusd(date: str = "")` - only for `USD`.
- `exhkd(date: str = "")` - only for `HKD`.

Example:
```python
>>> CJ = get_cookies()
>>> sess = get_session()
>>> clean_html("<span>hello.</span>")
hello.
>>> check_symbol(601318)
"SH601318"
>>> exrate("2019-01-10", "EUR")
[7.8765, 7.8443]
>>> exusd(date="2019-01-10")
[6.816, 6.8526]
>>> exhkd("2019-01-10")
[0.86959, 0.87419]
```