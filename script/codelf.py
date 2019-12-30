# -*- coding: utf-8 -*-
# ===========================================================================
# FileName: search.py
# Description: Search usage variable names from https://unbug.github.io/codelf/
# Author: voldikss
# GitHub: https://github.com/voldikss
# ===========================================================================

import codecs
import json
import re
import sys
if sys.version_info[0] < 3:
    is_py3 = False
    reload(sys)
    sys.setdefaultencoding('utf-8')
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr)
    from urlparse import urlparse
    from urllib import urlencode
    from urllib import quote_plus as url_quote
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib2 import HTTPError
else:
    is_py3 = True
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    from urllib.parse import urlencode
    from urllib.parse import quote_plus as url_quote
    from urllib.parse import urlparse
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.error import HTTPError


CODELF_API = 'https://searchcode.com/api/codesearch_I/?callback=searchcodeRequestVariableCallback&p=0&per_page=42&q='
YOUDAO_API = 'https://fanyi.youdao.com/openapi.do?callback=youdaoFanyiRequestCallback&keyfrom=Codelf&key=2023743559&type=data&doctype=jsonp&version=1.1&q='
FILTER_WORDS = ['at', 'are', 'am', 'the', 'of', 'at', 'a', 'an', 'is', 'not', 'no', 'a', 'b', 'c', 'd', 'e',
                'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


def search(words):
    if is_chinese(words):
        words = translate(words)
    url = CODELF_API + url_quote(words)
    r_json = http_request(url)
    if r_json:
        search_callback(r_json, words)


def search_callback(r_json, words):
    res = json.loads(r_json)
    result = []
    for item in res['results']:
        for lnum in item['lines']:
            line = item['lines'][lnum]
            line = re.sub(r'[^a-zA-Z_\-]+', ' ', line).strip()
            for target in words.split():
                for word in re.split(r'\s+', line):
                    if target.lower() in word.lower() and word not in result:
                        result.append(word)
    sys.stdout.write(str(result))


def translate(zh_str):
    url = YOUDAO_API + url_quote(zh_str)
    res = http_request(url)
    if res:
        json_str = res[27:-2]
        r_json = json.loads(json_str)
        return translate_callback(r_json)


def translate_callback(r_json):
    if 'translation' in r_json:
        translation = r_json['translation'][0]
    elif 'explain' in r_json:
        translation = r_json['explain'][0]
    else:
        return ''
    return ''.join(filter(lambda x: x.lower() not in FILTER_WORDS, translation.split()))


def is_chinese(s):
    return all([u'\u4e00' <= ch <= u'\u9fff' for ch in s])


def http_request(url):
    req = Request(url)
    try:
        res = urlopen(req, timeout=5)
    except (URLError, HTTPError):
        return None
    return res.read().decode('utf-8')


if __name__ == '__main__':
    search(''.join(sys.argv[1:]))
    # search('图片')
    # translate('图片')
