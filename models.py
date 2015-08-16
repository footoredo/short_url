#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
from libs import short_url
import string
import random
import MySQLdb as mdb
import settings

debug = settings.DEBUG

class DB(object):
    def __init__(self):
        self.db = mdb.connect('localhost', 'shorturl', 'bombaycat', 'shorturl')
        self.cursor = self.db.cursor()

    def get_info(self):
        if debug:
            return self.cursor.execute("select * from map")
        else:
            return ""

    def exist_url(self, short_url):
        return self.cursor.execute("select * from map where shorten='%s'" % short_url)

    def generate_url(self):
        sigma = string.letters + string.digits

        short_url = ''.join(random.sample(sigma, 6))
        while (self.exist_url(short_url)):
            short_url = ''.join(random.sample(sigma, 6))

        return short_url

    def add_url(self, short_url, long_url):
        """添加 URL
        """
        self.cursor.execute("insert into map values('%s','%s')" % (short_url, long_url))
        self.db.commit()

    def get_expand(self, short_url):
        """根据短 URL 返回原始 URL
        """
        self.cursor.execute("select url from map where shorten='%s'" % (short_url))
        return self.cursor.fetchone()
