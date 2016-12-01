from trading import config
from trading import util

import ClientCookie
import mechanize 
import urllib2
import urllib

class FetchLater(Exception):
    pass

class Browser(mechanize.Browser):

    def __init__ (self, user_agent=None, *a, **kw):
        mechanize.Browser.__init__(self, *a, **kw)
        user_agent = user_agent or 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3'
        self._cj = cj = ClientCookie.LWPCookieJar()
        try:
            cj.load(config.COOKIE_FILE)
        except IOError:
            pass
        self.set_cookiejar(cj)
        self.set_handle_robots(False)
        self.addheaders=[('User-Agent', user_agent)]

    def follow_link(self, link=None, **kw):
        util.debug("Browser.follow_link: %s (%s)" % (link, kw))
        return mechanize.Browser.follow_link(self, link, **kw)

    def open(self, url, **data):
        util.debug("Browser.open: %s (%s)" % (url, data))
        if data:
            data = urllib.urlencode(data)
        else:
            data = None
        url = self._normalize(url)
        return mechanize.Browser.open(self, url, data=data)

    def _normalize(self, url):
        """urllib2? infrastructure doesn't seem to care about spaces in URLs"""
        def norm(t):
            return t.replace(' ', '%20') #XXX escape more stuff?
        if isinstance(url, urllib2.Request):
            data = url.data
            headers = url.headers
            origin_req_host = url.origin_req_host
            unverifiable = url.unverifiable
            url = norm(url.get_full_url())
            url = urllib2.Request(url, data=data, headers=headers,
                                 origin_req_host=origin_req_host,
                                 unverifiable=unverifiable)
        elif type(url) is str:
            url = norm(url)
        return url

    def save_cookies(self):
        self._cj.save(config.COOKIE_FILE)

    def fetch(self, method, args=(), kwargs={}):
        fct = getattr(self, method, None)
        assert fct is not None
        assert method in ('open', 'follow_link')
        try:
            fct(*args, **kwargs)
            data = self.response().read()
            self.response().seek(0)
            title = None
            if self.viewing_html():
                title = self.title()
            return data, title
        except urllib2.HTTPError, e:
            print "XXX: %s" % e
            raise FetchLater()
