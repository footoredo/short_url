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
        self.config = settings.DB_CONFIG
        self.db = mdb.connect(**self.config);
        self.cursor = self.db.cursor()
        self.words = dict(adjectives=[], nouns=[])
        adjectives_list = open(settings.WORDS_LIST["ADJECTIVES_LIST"], "r")
        nouns_list = open(settings.WORDS_LIST["NOUNS_LIST"], "r")
        self.adjectives = [adjective.strip() for adjective in adjectives_list]
        self.nouns = [noun.strip() for noun in nouns_list]
        adjectives_list.close()
        nouns_list.close()

    def check_connection(self):
        try:
            self.db.ping(True)
        except mdb.OperationalError:
            self.db = mdb.connect(**self.config);
            self.cursor = self.db.cursor()

    def get_info(self):
        if debug:
            self.check_connection()
            return self.cursor.execute("select * from map")
        else:
            return ""

    def exist_url(self, short_url):
        self.check_connection()
        return self.cursor.execute("select * from map where shorten=%s" , short_url)

    def generate_url(self):
#sigma = string.letters + string.digits

        self.check_connection()
        short_url = random.choice(self.adjectives) + '-' + random.choice(self.nouns)
        while (self.exist_url(short_url)):
            short_url = random.choice(self.adjectives) + '-' + random.choice(self.nouns)

        return short_url

    def add_url(self, short_url, long_url):
        """添加 URL
        """
        self.check_connection()
        self.cursor.execute("insert into map values(%s,%s)" , (short_url, long_url))
        self.db.commit()

    def get_expand(self, short_url):
        """根据短 URL 返回原始 URL
        """
        self.check_connection()
        self.cursor.execute("select url from map where shorten=%s" , (short_url))
        return self.cursor.fetchone()

    def exist_code(self, code):
        self.check_connection()
        return self.cursor.execute("select code from codes where code=%s" , (code))

    def add_code(self, code):
        self.check_connection()
        self.cursor.execute("insert into codes values(%s)" , code)
        self.db.commit()
    
    def delete_code(self, code):
        self.check_connection()
        self.cursor.execute("delete from codes where code=%s" , code)
        self.db.commit()

    def generate_code(self):
        sigma = string.letters + string.digits

        self.check_connection()
        code = ''.join(random.sample(sigma, 8))
        while (self.exist_code(code)):
            code = ''.join(random.sample(sigma, 8))

        self.add_code(code)

        return code
