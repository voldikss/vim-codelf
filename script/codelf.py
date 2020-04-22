# -*- coding: utf-8 -*-
# ===========================================================================
# FileName: search.py
# Description: Search usage variable names from https://unbug.github.io/codelf/
# Author: voldikss
# GitHub: https://github.com/voldikss
# ===========================================================================

import codecs
import argparse
import json
import time
import socket
import random
import re
import sys

if sys.version_info[0] < 3:
    is_py3 = False
    reload(sys)
    sys.setdefaultencoding("utf-8")
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr)
    from urlparse import urlparse
    from urllib import urlencode
    from urllib import quote_plus as url_quote
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib2 import HTTPError
else:
    is_py3 = True
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer)
    from urllib.parse import urlencode
    from urllib.parse import quote_plus as url_quote
    from urllib.parse import urlparse
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.error import HTTPError


CODELF_API = "https://searchcode.com/api/codesearch_I/?callback=searchcodeRequestVariableCallback&p=0&per_page=42&q="
FILTER_WORDS = [
    "at",
    "are",
    "am",
    "the",
    "of",
    "at",
    "a",
    "an",
    "is",
    "not",
    "no",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]


class Base:
    def http_request(self, url, data=None, headers=None):
        if data:
            req = Request(url, data, headers)
        else:
            req = Request(url, headers)
        try:
            res = urlopen(req, timeout=10)
        except (URLError, HTTPError, socket.timeout):
            return None
        return res.read().decode("utf-8")

    def set_proxy(self, proxy_url=None):
        try:
            import socks
        except ImportError:
            sys.stderr.write("pySocks module should be installed\n")
            return None

        try:
            import ssl

            ssl._create_default_https_context = ssl._create_unverified_context
        except Exception:
            pass

        self._proxy_url = proxy_url

        proxy_types = {
            "http": socks.PROXY_TYPE_HTTP,
            "socks": socks.PROXY_TYPE_SOCKS4,
            "socks4": socks.PROXY_TYPE_SOCKS4,
            "socks5": socks.PROXY_TYPE_SOCKS5,
        }

        url_component = urlparse(proxy_url)

        proxy_args = {
            "proxy_type": proxy_types[url_component.scheme],
            "addr": url_component.hostname,
            "port": url_component.port,
            "username": url_component.username,
            "password": url_component.password,
        }

        socks.set_default_proxy(**proxy_args)
        socket.socket = socks.socksocket

    def test_request(self, test_url):
        print("test url: %s" % test_url)
        print(self.http_request(test_url))


class YoudaoTranslator(Base):
    def __init__(self):
        self.url = (
            "https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule"
        )
        self.D = "97_3(jkMYg@T[KZQmqjTK"

    def get_md5(self, value):
        import hashlib

        m = hashlib.md5()
        m.update(value.encode("utf-8"))
        return m.hexdigest()

    def sign(self, text, salt):
        s = "fanyideskweb" + text + salt + self.D
        return self.get_md5(s)

    def callback(self, r_json):
        paraphrase = self.get_paraphrase(r_json)
        if paraphrase:
            translation = paraphrase
        else:
            explain = self.get_explain(r_json)
            if len(explain) == 0:
                return None
            translation = explain[0]
        return "".join(
            filter(lambda x: x.lower() not in FILTER_WORDS, translation.split())
        )

    def translate(self, text):
        self.text = text
        salt = str(int(time.time() * 1000) + random.randint(0, 10))
        sign = self.sign(text, salt)
        header = {
            "Cookie": "OUTFOX_SEARCH_USER_ID=-2022895048@10.168.8.76;",
            "Referer": "http://fanyi.youdao.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.2; rv:51.0) Gecko/20100101 Firefox/51.0",
        }
        data = {
            "i": text,
            "from": "zh",
            "to": "en",
            "smartresult": "dict",
            "client": "fanyideskweb",
            "salt": salt,
            "sign": sign,
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "action": "FY_BY_CL1CKBUTTON",
            "typoResult": "true",
        }

        data = urlencode(data).encode("utf-8")
        res = self.http_request(self.url, data, header)
        r_json = json.loads(res)
        return self.callback(r_json)

    def get_paraphrase(self, obj):
        translation = ""
        t = obj.get("translateResult")
        if t:
            for n in t:
                part = []
                for m in n:
                    x = m.get("tgt")
                    if x:
                        part.append(x)
                if part:
                    translation += ", ".join(part)
        return translation

    def get_explain(self, obj):
        explain = []
        if "smartResult" in obj:
            smarts = obj["smartResult"]["entries"]
            for entry in smarts:
                if entry:
                    entry = entry.replace("\r", "")
                    entry = entry.replace("\n", "")
                    explain.append(entry)
        return explain


class Codelf(Base):
    def search(self, word):
        if self.is_chinese(word):
            translator = YoudaoTranslator()
            word = translator.translate(word)
        url = CODELF_API + url_quote(word)
        r_json = self.http_request(url)
        if r_json:
            self.callback(r_json, word)
        else:
            sys.stdout.write(str([word]))

    def callback(self, r_json, word):
        res = json.loads(r_json)
        result = []
        for item in res["results"]:
            for lnum in item["lines"]:
                line = item["lines"][lnum]
                line = re.sub(r"[^a-zA-Z_\-]+", " ", line).strip()
                for target in word.split():
                    for w in re.split(r"\s+", line):
                        if target.lower() in w.lower() and w not in result:
                            result.append(w)
        sys.stdout.write(str(result))

    def is_chinese(self, s):
        return any([u"\u4e00" <= ch <= u"\u9fff" for ch in s])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True)
    parser.add_argument("--proxy", required=False)
    args = parser.parse_args()

    text = args.text.strip("'")
    text = text.strip('"')
    text = text.strip()
    proxy = args.proxy

    codelf = Codelf()
    if proxy:
        codelf.set_proxy(proxy)

    codelf.search(text)


if __name__ == "__main__":

    def test_proxy():
        t = Base()
        t.set_proxy("http://localhost:8087")
        t.test_request("https://www.google.com")

    def test_codelf():
        codelf = Codelf()
        codelf.search("图片")

    def test_youdao():
        translator = YoudaoTranslator()
        res = translator.translate("图片")
        print(res)

    # test_codelf()
    # test_youdao()
    main()
