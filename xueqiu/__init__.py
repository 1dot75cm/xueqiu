# -*- coding: utf-8 -*-

"""
xueqiu.api
~~~~~~~~~~

This module implements a humanize XueQiu API wrappers.

:copyright: (c) 2019 by 1dot75cm.
:license: MIT, see LICENSE for more details.
"""

# xueqiu api
from .model import news
from .model import search
from .model import Selector
from .model import Stock
from .model import Fund
from .model import Post
from .model import Comment
from .model import User
# funds api
from .model import get_all_funds
from .model import get_all_funds_ranking
# economic api
from .model import get_economic
from .model import get_economic_of_china
# others
from .model import get_data_yahoo
from .model import get_quote_yahoo
from .model import get_stock_margin
from .model import get_hsgt_history
from .model import get_hsgt_top10
from .model import get_hsgt_holding
# baidu search index
from .baidu import BaiduIndex


__pkgname__ = "xueqiu"
__version__ = "0.1.3"
__license__ = "MIT"
__url__ = "https://github.com/1dot75cm/xueqiu"
__descript__ = "A humanize XueQiu API wrappers."
__author__ = "1dot75cm"
__email__ = "sensor.wen@gmail.com"


def main():
    me = f"""{__pkgname__} {__version__} - {__descript__}

:copyright: (c) 2019 by {__author__}.
:license: {__license__}, see LICENSE for more details."""
    print(me)


if __name__ == '__main__':
    main()