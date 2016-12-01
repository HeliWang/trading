from trading.browser import FetchLater
from trading import parser
from trading import util
from trading import config

from trading.htmlgen import T

import os
import time
import random

class _Page(object):
    def __init__(self, archive):
        """archive = None disables caching"""
        self.archive = archive
        self.valid = True
        self.initialized = False

    def url(self):
        raise NotImplementedError

    def url_args(self):
        return {}

    def cache_fn(self):
        'return relative_name_in_archive'
        raise NotImplementedError

    def _validate(self, data, title):
        self.valid = True
        if not data:
            self.valid = False

    def _sanitize(self, data):
        data = data.replace('scr"+"ipt', "script")
        data = data.replace('scr" + "ipt', "script")
        data = data.replace("scri' + 'pt", "script")
        data = data.replace('/scr" + "ipt', "script")
        data = data.replace('ifr"+"ame', "iframe")
        data = data.replace('ifr" + "ame', "iframe")
        data = data.replace("ifra' + 'me", "iframe")
        data = data.replace('/ifr" + "ame', "iframe")
        return data

    def fetch(self, browser, force=False, obfuscate=0):
        if force or not self.is_cached():
            sleep_for = random.random() * obfuscate
            util.debug('. sleep for: %.2f seconds (obfuscate=%d)' % 
                (sleep_for, obfuscate))
            time.sleep(sleep_for)
            data, title = browser.fetch('open', args=(self.url(),), kwargs=self.url_args())
            self._validate(self._sanitize(data), title)
            self._save(data)
        else:
            title = None
            a = util.ZipFile(self.archive, mode='r')
            data = a.read(self.cache_fn())
            data = self._sanitize(data)
            a.close()
            try:
                self._validate(data, title)
            except FetchLater:
                pass
        return data

    def is_cached(self):
        if self.archive is None:
            return False
        if not os.path.exists(self.archive):
            return False
        a = util.ZipFile(self.archive, mode='r')
        result = self.cache_fn() in a.namelist()
        a.close()
        return result

    def _save(self, data, filename=None):
        if self.archive is not None:
            mode = os.path.exists(self.archive) and 'a' or 'w'
            a = util.ZipFile(self.archive, mode=mode)
            filename = filename or self.cache_fn()
            filename = filename.encode('ascii')
            util.debug("file://%s in (%s)" % (filename, self.archive))
            # get rid of entries with same filename (overwrite old data)
            delete = []
            for i, e in enumerate(a.filelist):
                if e.filename == filename:
                    delete.append(i)
            for i in delete:
                del a.filelist[i]
            a.writestr(filename, data)
            a.close()


class RawPage(_Page):

    def __init__(self, archive, url, filename):
        super(RawPage, self).__init__(archive)
        self._url = url
        self.filename = filename

    def cache_fn(self):
        if self.archive is None:
            return None
        return self.filename

    def url(self):
        return self._url

class SymbolPage(_Page):
    """A page related to a symbol. Constructor's second argument is always the
       ticker for the symbol.
    """

    CachePrefix = None
    CacheExtension = "html"
    _URL = None

    def __init__(self, archive, name):
        super(SymbolPage, self).__init__(archive)
        self.name = name

# #ifndef VERSION_SPIDER
    def _init(self, data):
        raise NotImplementedError

    def init(self, data=None, force=False): # open(s.cache_fn()).read() or 
                                            # return value of fetch()
        if force or not self.initialized:
            if data is None:
                if self.is_cached():
                    a = util.ZipFile(self.archive)
                    data = a.read(self.cache_fn())
                    a.close()
                else:
                    self.valid = False
                    return
            data = self._sanitize(data)
            try:
                self._validate(data, None)
            except FetchLater:
                pass
            if self.valid:
                self._init(data)
            self.initialized = True
# #endif

    def url(self):
        return self._URL % self.name

    def url2(self, link = None):
        link = link or self.__class__.__name__
        return T.a(href=self._URL % self.name)[T.b[link]]

    def cache_fn(self):
        assert self.CachePrefix
        if self.archive is None:
            return None
        fn = "%s_%s.%s" % (self.CachePrefix, self.name, self.CacheExtension)
        return fn


class MultiPage(SymbolPage):
    "One root page (same as `SymbolPage`) with N following pages"

    DefaultStopAfter = None

    def __init__(self, archive, name, stop_after=None):
        super(MultiPage, self).__init__(archive, name)
        self.stop_after = stop_after or self.DefaultStopAfter

    def _parse(self, parser):
        raise NotImplementedError

    def init(self, data=[], force=False):
        if force or not self.initialized:
            try:
                if not data:
                    if not self.is_cached():
                        self.valid = False
                        return
                    a = util.ZipFile(self.archive)
                    data = [a.read(fn) for fn in self.cache_fns()]
                    a.close()
                    try:
                        map(lambda d: self._validate(d, None), data)
                    except FetchLater:
                        pass
                    if self.valid: 
                        for d in data:
                            p = parser.parse(d)
                            self._parse(p)
            except StopIteration:
                pass
            self.initialized = True

    def fetch(self, browser, force=False, obfuscate=0):
        if not force and self.is_cached():
            a = util.ZipFile(self.archive)
            data = [a.read(fn) for fn in self.cache_fns()]
            a.close()
            return data
        result = []
        i = 1 
        method = 'open'
        args = (self.url(),)
        kwargs = {}
        fn = self.cache_fn()
        while 1:
            sleep_for = random.random() * obfuscate
            util.debug('. sleep for: %.2f seconds' % sleep_for)
            time.sleep(sleep_for)
            data, title = browser.fetch(method, args, kwargs)
            self._validate(data, title)
            self._save(data, filename=fn)
            result.append(data)
            try:
                method, args, kwargs = self._parse(parser.parse(data))
            except StopIteration:
                break
            if self.stop_after is not None and self.stop_after == i:
                break
            fn = self.cache_fn(i)
            #if i == 1 and obfuscate > 4: 
            #    be faster when following links on the main page
            #    don't be any faster then 4 seconds :)
            #    obfuscate /= 2.
            i += 1
        return result

    def cache_fn(self, index=None):
        assert self.CachePrefix
        if self.archive is None:
            return None
        if index is None:
            return super(MultiPage, self).cache_fn()
        fn = "%s_%s_%d.%s" % (self.CachePrefix, self.name, index,
                              self.CacheExtension)
        return fn

    def cache_fns(self):
        if self.archive is None:
            return None
        result = [self.cache_fn()]
        i = 1
        a = util.ZipFile(self.archive, mode='r')
        while 1:
            if self.stop_after is not None and i == self.stop_after:
                break
            name = self.cache_fn(index=i)
            if not name in a.namelist():
                break
            result.append(name)
            i+=1
        a.close()
        return result


class BinaryPage(SymbolPage):
    CacheExtension = "png"

# #ifndef VERSION_SPIDER
    def _init(self, data):
        pass
# #endif
