# -*- coding: latin-1 -*-
import sys, os
import re
import urllib
import urllib2
import urlparse
from urlparse import ParseResult
try:
    import xbmc, xbmcvfs, xbmcgui, xbmcaddon
except:
    pass

def patch_unquote():
    urllib.unquote = unquote
    urllib2.unquote = unquote
    urlparse.unquote = unquote
    urllib.unquote_plus = unquote_plus
    urllib.quote_plus = quote_plus
    urllib.quote = quote


def unquote_to_bytearray(s):
    parts = s.split("%")
    if len(parts) == 1:
        return s  # no unquoting needed

    result = bytearray(parts[0])

    # Process pair-wise hex characters and add them to the byte array
    for item in parts[1:]:
        try:
            result.append(int(item[:2], 16))  # hex part
            for x in item[2:]:
                result.append(x)  # non-hex part
        except ValueError:
            # Invalid hex digit, copy over invalid value verbatim
            result.append("%")
            for x in item:
                result.append(x)

    return result


def unquote_plus(s):
    return unpercent(str(unquote(s)))


def unpercent(s):
    url = str(s).replace("&quot;", "%22")
    url = url.replace("http%3A%2F%2F", "http://")
    url = url.replace("%20", "%2B")
    url = url.replace('%22', '"')
    url = url.replace('%2C', ',')
    url = url.replace("%27", "'")
    url = url.replace("%3A", ":")
    url = url.replace("%3B", ";")
    url = url.replace("%26", "&")
    url = url.replace("%3F", "?")
    url = url.replace("%2F", "/")
    url = url.replace("%5C", "\\")
    url = url.replace("%2B", "+")
    url = url.replace("%26amp%3B", "&amp;")
    url = url.replace("%26", "&")
    url = url.replace("%22", "&quot;")
    url = url.replace(" ", "+")
    return str(url)


def unquote(s, encoding="utf-8", errors="replace"):
    """Unquote a percent-encoded string."""
    if isinstance(s, unicode):
        s = s.encode(encoding, errors)
        barray = unquote_to_bytearray(s)
        return barray.decode(encoding, errors)

    barray = unquote_to_bytearray(s)
    return str(barray)


def escape(st):
    return st.replace('\\', r'\\').replace('\t', r'\t').replace('\r', r'\r').replace('\n', r'\n').replace('\"', r'\"')


def unescape(s):
    if '&' not in s:
        return s
    def replaceEntities(s):
        s = s.groups()[0]
        try:
            if s[0] == "#":
                s = s[1:]
                if s[0] in ['x', 'X']:
                    c = int(s[1:], 16)
                else:
                    c = int(s)
                return unichr(c)
        except ValueError:
            return '&#' + s + ';'
        else:
            from htmlentitydefs import entitydefs, name2codepoint
            if entitydefs is None:
                # entitydefs = \
                entitydefs = {'apos': u"'"}
                for k, v in name2codepoint.iteritems():
                    entitydefs[k] = unichr(v)
            try:
                return entitydefs[s]
            except KeyError:
                return '&' + s + ';'

    return re.sub(r"&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));", replaceEntities, s)


def bareDecode(s):
    return unpercent(unquote_plus(s))

def bareEncode(s):
    url = unpercent(escape(s))
    return str(urllib.quote_plus(url))

def bareEscape(s):
    url = unpercent(escape(s))
    return str(url)

def bareUnescape(s):
    url = unquote_plus(unescape(s))
    return unpercent(url)

def quote_plus(s):
    return str(quote_plus(s))

def quote(s):
    return str(quote(escape(s))).replace("http%3A%2F%2F", "http://")