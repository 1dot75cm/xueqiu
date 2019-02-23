# -*- coding: utf-8 -*-

"""
xueqiu.api
~~~~~~~~~~

This module contains some XueQiu API strings.

:copyright: (c) 2019 by 1dot75cm.
:license: MIT, see LICENSE for more details.
"""

import os
import platform

# prefix
prefix = "https://xueqiu.com"
prefix2 = "https://stock.xueqiu.com"
prefix3 = "https://api.xueqiu.com"
prefix4 = "https://danjuanapp.com"
prefix5 = "http://fundf10.eastmoney.com"
invest = "https://cn.investing.com"
homedir = os.getenv('TESTDIR') or os.getenv('HOME') or os.getenv('LOCALAPPDATA')
cookie_file = platform.system() == "Linux" and \
    os.path.join(homedir, ".xueqiu", "cookie") or \
    os.path.join(homedir or "", "xueqiu", "cookie")  # linux or windows

# stock
stock_quote = prefix2 + "/v5/stock/quote.json?symbol=%s&extend=detail"  # 基本信息
stock_quotec_v5 = prefix2 + "/v5/stock/realtime/quotec.json?symbol=%s"  # 实时行情(多参)
stock_quotec_v4 = prefix + "/v4/stock/quotec.json?code=%s"
stocks_quote_v5 = prefix2 + "/v5/stock/batch/quote.json?symbol=%s"  # 多股信息(多参)
stocks_quote_v4 = prefix + "/v4/stock/quote.json?code=%s"
# https://stock.xueqiu.com/v5/stock/chart/minute.json?symbol=.DJI&period=1d  # 分时行情
stock_history = prefix2 + "/v5/stock/chart/kline.json?symbol=%s&begin=%s000&end=%s000&period=%s&type=before&indicator=%s"  # 历史行情
# period: day week month quarter year 120m 60m 30m 15m 5m 1m; indicator: kline,ma,macd,kdj,boll,rsi,wr,bias,cci,psy,pe,pb,ps,pcf,market_capital
# https://stock.xueqiu.com/v5/stock/history/trade.json?symbol=TSLA&count=20  # 成交明细
#stock_follows = prefix + "/recommend/pofriends.json?type=1&code=%s&start=0&count=14"  # 股票粉丝
stock_follows = prefix3 + "/friendships/stockfollowers.json?x=0.75&code=%s&pageNo=%s&size=%s"  # 股票粉丝
stock_popstocks = prefix + "/stock/portfolio/popstocks.json?code=%s&start=0&count=%s"  # 粉丝关注股票
stock_industry = prefix + "/stock/industry/stockList.json?code=%s&type=1&size=%s"  # 同行业股票
hot_stocks = prefix2 + "/v5/stock/hot_stock/list.json?type=%s&size=%s"  # 热门股票
pro_users = prefix + "/recommend/user/stock_hot_user.json?symbol=%s&start=0&count=%s"  # 专业用户
# type 全球10 沪深12 港股13 美股11
user_stocks = prefix2 + "/v5/stock/portfolio/stock/list.json?uid=%s&pid=-%s&category=1&size=%s" # 用户关注
# pid 全球1, 沪深5, 港股7, 美股6

# stock sheet
#api.xueqiu.com/stock/f10/balsheet.csv?symbol=SH601318&page=1&size=1000
#api.xueqiu.com/stock/f10/incstatement.csv?symbol=SH601318&page=1&size=1000
#api.xueqiu.com/stock/f10/cfstatement.csv?symbol=SH601318&page=1&size=1000
income = prefix2 + "/v5/stock/finance/%s/income.json?symbol=%s&type=%s&is_detail=true&count=%s"  # 利润
balance = prefix2 + "/v5/stock/finance/%s/balance.json?symbol=%s&type=%s&is_detail=true&count=%s"  # 资产
cash_flow = prefix2 + "/v5/stock/finance/%s/cash_flow.json?symbol=%s&type=%s&is_detail=true&count=%s"  # 现金
indicator = prefix2 + "/v5/stock/finance/%s/indicator.json?symbol=%s&type=%s&is_detail=true&count=%s"  # 主要指标
#/v5/stock/finance/cn/special_indicator.json?count=5&type=&symbol=SH601318  # 专项指标
business = prefix2 + "/v5/stock/finance/%s/business.json?symbol=%s&is_detail=true&count=%s"  # 主营业务构成

# stock summary
# A股 主要指标 行业 概念 公司简介 行业对比 股本股东 公司高管 分红融资 机构持仓 经营评述
# 港股 主要指标 行业 公司简介 股本股东 公司高管 持股变动 分红派息
# 美股 主要指标 概念 公司简介 股本股东 公司高管 持股变动 分红派息 机构持仓
f10_indicator = prefix2 + "/v5/stock/f10/%s/indicator.json?symbol=%s"  # |主要指标
f10_industry = prefix2 + "/v5/stock/f10/%s/industry.json?symbol=%s"  # |行业
#概念/v5/stock/f10/%s/concept.json?symbol=SZ000725&ind_code=00031590
f10_company = prefix2 + "/v5/stock/f10/%s/company.json?symbol=%s"  # |公司简介
f10_industry_compare = prefix2 + "/v5/stock/f10/%s/industry/compare.json?type=all&symbol=%s"  # |行业对比
f10_shareschg = prefix2 + "/v5/stock/f10/%s/shareschg.json?symbol=%s"  # 股本变动 |股本股东
f10_holders = prefix2 + "/v5/stock/f10/%s/holders.json?symbol=%s"  # 股东人数
f10_top_holders = prefix2 + "/v5/stock/f10/%s/top_holders.json?circula=1&symbol=%s"  # 十大股东0 十大流通股东1
f10_skholder = prefix2 + "/v5/stock/f10/%s/skholder.json?symbol=%s"  # 高管简介 |公司高管
f10_skholderchg = prefix2 + "/v5/stock/f10/%s/skholderchg.json?symbol=%s"  # 高管增减持
f10_bonus = prefix2 + "/v5/stock/f10/%s/bonus.json?size=100&page=1&symbol=%s"  # 分红增发配股 |分红融资
f10_org_change = prefix2 + "/v5/stock/f10/%s/org_holding/change.json?symbol=%s"  # 机构持仓汇总 |机构持仓
f10_org_detail = prefix2 + "/v5/stock/f10/%s/org_holding/detail.json?symbol=%s"  # 机构持仓明细
f10_business_analysis = prefix2 + "/v5/stock/f10/%s/business_analysis.json?size=20&page=1&symbol=%s"  # |经营评述
margin = "http://dcfm.eastmoney.com/EM_MutiSvcExpandInterface/api/js/get"  # 融资融券

# fund
exrate = "http://www.chinamoney.com.cn/r/cms/www/chinamoney/data/fx/ccpr-notice%s.json"
_exrate = "http://www.chinamoney.com.cn/r/cms/www/chinamoney/data/fx/ccpr.json"
fund_nav = prefix5 + "/F10DataApi.aspx?type=lsjz&code=%s&page=1&per=1"  # 基金净值
#/djapi/fund/nav/history/%s?page=%s&size=%s
fund_history = prefix5 + "/F10DataApi.aspx?type=lsjz&code=%s&sdate=%s&edate=%s&per=%s"  # 历史净值
fund_stocks = prefix5 + "/FundArchivesDatas.aspx?type=jjcc&code=%s&topline=50&year=%s&month=%s"  # 基金持仓
all_funds = "http://fund.eastmoney.com/js/fundcode_search.js"  # 所有基金
all_funds_rank = "http://fund.eastmoney.com/data/rankhandler.aspx"  # 基金排行
#all_comp "http://fund.eastmoney.com/js/jjjz_gs.js"  # 所有基金公司

# selector
selector = prefix + "/stock/screener/screen.json"
select_areas = prefix + "/stock/screener/areas.json"  # 地区
select_industries = prefix + "/stock/screener/industries.json?category=%s"  # 行业
select_fields = prefix + "/stock/screener/fields.json?category=%s"  # 指标
# https://xueqiu.com/stock/screener/values.json?category=SH&field=follow7d

# user, article
# login https://github.com/Rockyzsu/xueqiu
send_code = prefix + "/account/sms/send_verification_code.json"  # post: areacode=86, telephone
user_login = prefix + "/snowman/login"  # post: username password, telephone code
comments = prefix + "/statuses/comments.json?id=%s&count=%s&page=%s&asc=%s"  # 评论
comment_like = prefix + "/comments/like.json"  # post: id
comment_unlike = prefix + "/comments/unlike.json"
user_page = prefix + "/statuses/original/show.json?user_id=%s"  # 个人信息
user_friends = prefix + "/friendships/groups/members.json?uid=%s&page=%s&gid=0"  # 关注
user_follows = prefix + "/friendships/followers.json?uid=%s&pageNo=%s"  # 粉丝
user_post = prefix + "/v4/statuses/user_timeline.json?user_id=%s&page=%s&count=%s"  # 帖子
user_article = prefix + "/statuses/original/timeline.json?user_id=%s&page=%s&count=%s"  # 专栏
user_favorite = prefix + "/favorites.json?userid=%s&page=%s&size=%s"  # 收藏文章
news = prefix + "/v4/statuses/public_timeline_by_category.json?since_id=-1&max_id=%s&category=%s&count=%s"  # 首页新闻
# category 头条-1, 今日话题0, 直播6, 沪深105, 港股102, 美股101, 基金104, 私募113, 房产111, 汽车114, 保险110
post_like = prefix + "/statuses/like.json"  # post: id
post_unlike = prefix + "/statuses/unlike.json"
post_favorite = prefix + "/favorites/create.json?id=%s"  # 收藏
post_unfavorite = prefix + "/favorites/destroy/%s.json"

# search
search_stock = prefix + "/stock/search.json?code=%s&size=%s&page=%s"
search_post = prefix + "/statuses/search.json?q=%s&symbol=%s&count=%s&page=%s&sort=%s&source=%s"
# sort=[time最新|reply评论|relevance默认] source=[all|user讨论|news新闻|notice公告|trans交易]
search_user = prefix + "/users/search.json?q=%s&count=%s&page=%s"
search_cube = prefix + "/cube/search.json?q=%s&count=%s&page=%s"

# xpath
x_post_content = "//div[@class='article__bd__detail']//text()"
x_post_json = "//script[contains(text(),'user_id')]/text()"
x_fund_stocks = r"\w{2,6}.html.*?(\w{2,6}).html.>(\w.+?)<.*?>(\d{1,2}.\d{2})%"
x_fund_nav = "//td/text()"
x_fund_history = r"(\d{4}-\d{2}-\d{2}).*?(\d+.\d+).*?(\d+.\d+).*?(-?\d+.\d{2})%"
x_exrate = r"\d{1,3}.\d{2,5}"

# economy
economic = "https://sbcharts.investing.com/events_charts/us/%s.json"  # 宏观经济数据
economic_search = invest + "/search/service/SearchInnerPage"
china_stats = "http://data.stats.gov.cn/easyquery.htm"  # 国家统计局数据
china_stats_adv = "http://data.stats.gov.cn/adv.htm"

# baiduindex
baidu_search_live = "http://index.baidu.com/api/LiveApi/getLive?region=&word="  # live
baidu_search_index = "http://index.baidu.com/api/SearchApi/index"  # 搜索指数
baidu_feed_index = "http://index.baidu.com/api/FeedSearchApi/getFeedIndex"  # 资讯指数
baidu_news_index = "http://index.baidu.com/api/NewsApi/getNewsIndex"  # 媒体指数
baidu_data_key = "http://index.baidu.com/Interface/api/ptbk"
baidu_region = "http://index.baidu.com/api/SearchApi/region"  # 地域分布
baidu_social = "http://index.baidu.com/api/SocialApi/getSocial"  # 社会属性