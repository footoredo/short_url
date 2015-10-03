#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from secured import secret_code, db_config

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))

DEBUG = False # 调试模式
TEMPLATE_DIR = os.path.join(SITE_ROOT, 'templates')  # 模板目录
BASE_TEMPLATE = 'base'  # 基础模板

# URL 映射
URLS = (
    '/', 'Index',
    '/fvck.it.html', 'Wosign',
    '/%s' % secret_code, 'GetCode',
    '/show', 'Show',
    '(/j)?/shorten', 'Shorten',
    '/j/expand', 'Expand',
    '/(.*)', 'Expand',
)

DB_CONFIG = db_config

WORDS_LIST = {
  "ADJECTIVES_LIST": "adjectives.list",
  "NOUNS_LIST": "nouns.list"
}
