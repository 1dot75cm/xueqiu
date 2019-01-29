# -*- coding: utf-8 -*-

import sys
import os

if not __package__:
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)

import xueqiu
xueqiu.main()
