#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import re
import web
import qrcode
import settings
import models
import sys
import datetime
import os

debug = web.config.debug = settings.DEBUG
render = web.template.render(settings.TEMPLATE_DIR,
                             base=settings.BASE_TEMPLATE)
app = web.application(settings.URLS, globals())
db = models.DB()

def notfound():
    return Exception(render.notfound())

class Wosign(object):
    def GET(self):
        return open('fvck.it.html','r').read()

class GetCode(object):
    def GET(self):
        #return render.getcode("124343243")
        return render.getcode(db.generate_code())

class Show(object):
    def GET(self):
        return db.get_info()

class Index(object):
    """首页"""
    def GET(self):
        return render.index()


class Shorten(object):
    """网址缩短结果页"""
    def __init__(self):
        self.db = db 

    def add_scheme(self, url):
        """给 URL 添加 scheme(qq.com -> http://qq.com)"""
        # 支持的 URL scheme
        # 常规 URL scheme
        scheme2 = re.compile(r'(?i)^[a-z][a-z0-9+.\-]*://')
        # 特殊 URL scheme
        scheme3 = ('git@', 'mailto:', 'javascript:', 'about:', 'opera:',
                   'afp:', 'aim:', 'apt:', 'attachment:', 'bitcoin:',
                   'callto:', 'cid:', 'data:', 'dav:', 'dns:', 'fax:', 'feed:',
                   'gg:', 'go:', 'gtalk:', 'h323:', 'iax:', 'im:', 'itms:',
                   'jar:', 'magnet:', 'maps:', 'message:', 'mid:', 'msnim:',
                   'mvn:', 'news:', 'palm:', 'paparazzi:', 'platform:',
                   'pres:', 'proxy:', 'psyc:', 'query:', 'session:', 'sip:',
                   'sips:', 'skype:', 'sms:', 'spotify:', 'steam:', 'tel:',
                   'things:', 'urn:', 'uuid:', 'view-source:', 'ws:', 'xfire:',
                   'xmpp:', 'ymsgr:', 'doi:',
                   )
        url_lower = url.lower()

        # 如果不包含规定的 URL scheme，则给网址添加 http:// 前缀
        scheme = scheme2.match(url_lower)
        if not scheme:
            for scheme in scheme3:
                url_splits = url_lower.split(scheme)
                if len(url_splits) > 1:
                    break
            else:
                url = 'http://' + url
        return url

    def qrcode_table(self, code, data, error_correct_level='H'):
        #return ""
        """生成 QR Code html 表格，可以通过 css 控制黑白块的显示"""
        if error_correct_level == 'L':
            error_correct_level = qrcode.constants.ERROR_CORRECT_L
        elif error_correct_level == 'M':
            error_correct_level = qrcode.constants.ERROR_CORRECT_M
        elif error_correct_level == 'Q':
            error_correct_level = qrcode.constants.ERROR_CORRECT_Q
        else:
            error_correct_level = qrcode.constants.ERROR_CORRECT_H

        qr = qrcode.QRCode(error_correction = error_correct_level)
        qr.add_data(data)
        qr.make(fit=True)

        """matrix = qr.get_matrix()
        html = '<table id="qrcode-table">'
        for r in xrange(len(matrix)):
            html += "<tr>"
            for c in xrange(len(matrix[r])):
                if matrix[r][c]:
                    html += '<td class="dark" />'
                else:
                    html += '<td class="white" />'
            html += '</tr>'
        html += '</table>'
        return html"""

        img = qr.make_image()
        file_path = './static/%s+%s.png' % ( datetime.datetime.now().strftime("%Y-%m-%d+%H:%M:%S"), code)
        img.save(file_path)
        return file_path

    def POST(self, get_json=False):
        url = web.input().long_url.strip()
        if not url:
            return web.badrequest()

        url = self.add_scheme(url)

        shorten = web.input().short_url.strip()
        code = web.input().code.strip()
        randomed = False
        if not shorten or self.db.exist_url(shorten) or ( len(shorten) <= 6 and not self.db.exist_code(code) ):
            shorten = self.db.generate_url()
            randomed = True

        if (len(code) > 0 and not randomed and len(shorten) <= 6):
            self.db.delete_code(code)

        self.db.add_url(shorten, url)
        code = shorten
        shorten = web.ctx.homedomain + '/' + code

        if get_json:
            # 返回 json 格式的数据
            web.header('Content-Type', 'application/json')
            return json.dumps({'shorten': shorten, 'expand': url})
        else:
            shortens = web.storage({'url': shorten,
                                    'qr_table': self.qrcode_table(code, shorten),
                                    })
            return render.shorten(shortens)


class Expand(object):
    """短网址跳转到相应的长网址"""
    def __init__(self):
        self.db = db

    def get_expand(self, shorten):
        result = self.db.get_expand(shorten)
        if result:
            return list(result)[0]
        else: 
            return None

    def GET(self, shorten):
        """解析短网址，并作 301 跳转"""
        if not shorten:
            return web.seeother('/')

        expand = self.get_expand(shorten)
        if debug:
            print repr(expand)
        if expand:
            return web.redirect(expand)  # 301 跳转
        else:
            return web.notfound()

    def POST(self):
        """解析短网址，返回 json 数据"""
        shorten = web.input(shorten='').shorten.encode('utf8').strip()
        web.header('Content-Type', 'application/json')

        # 判断是否为有效短网址字符串
        if shorten and re.match('[a-zA-Z0-9]{5,}$', str(shorten)):
            expand = self.get_expand(shorten)

            if debug:
                print repr(expand)
            if expand:
                shorten = web.ctx.homedomain + '/' + shorten
                return json.dumps({'shorten': shorten, 'expand': expand})
            else:
                return json.dumps({'shorten': '', 'expand': ''})
        else:
            return json.dumps({'shorten': '', 'expand': ''})


if __name__ == '__main__':
    # 下面这条语句用于在服务器端通过 nginx + fastcgi 部署 web.py 应用
#sys.path.append(os.path.realpath(os.path.dirname(__file__))) 
    app.notfound = notfound
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
