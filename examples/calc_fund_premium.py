# -*- coding: utf-8 -*-
"""Calculate fund premium."""

from xueqiu import Fund

tasks = ['501301', '501021']
funds = [Fund(i) for i in tasks]

for i in funds:
    i.get_fund_stocks()
    i.calc_premium()

title = "{:<8}"*7
tkey = ['名称','现价','昨收','净值','估值','涨跌幅','溢价率']
data = "{:<7}{:<10}{:<10}{:<10}{:<10}{:<10.2%}{:.2%}"

print(title.format(*tkey))
for i in funds:
    print(data.format(i.name, i.current, i.last_close, i.fund_nav[1],
        i.fund_nav_guess[0], i.fund_nav_guess[1], i.fund_nav_premium))