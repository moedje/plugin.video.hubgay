# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json, datetime
import calendar
from calendar import month_name, month_abbr
import os.path as path
import re
import urllib
import urlquick
from urlquick import get as UrlGet
try:
    import urllib2
except:
    pass

#from kodiswift import Plugin, xbmc, ListItem, download_page, clean_dict, SortMethod
from xbmcswift2 import Plugin, xbmc, ListItem, download_page, clean_dict, SortMethod, common
from xbmcswift2.common import download_page as DL

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

plugin = Plugin()
__addondir__ = xbmc.translatePath(plugin.addon.getAddonInfo('path'))
__resdir__ = path.join(__addondir__, 'resources')
__imgsearch__ = path.join(__resdir__, 'search.png')
lstSorts = [SortMethod.UNSORTED, SortMethod.LABEL]
HTML = None
try:
    from HTMLParser import HTMLParser
    HTML = HTMLParser()
except:
    HTML = None

def makeVideoItems(itemlist, sitename=None):
    """
    Takes a list of dict's returned from the API and looks for the specific fields to build XBMC ListItem for each item
    :param itemlist:
    :return: List of dict(Label, Label2, Icon, Thumb, Path) items created for each dict returned from the API
    """
    litems = []
    allitems = []
    vitem = dict()
    vid = dict()
    item = dict()
    SKIP = False
    try:
        for vitem in itemlist:
            assert isinstance(vitem, dict)
            vitem = clean_dict(vitem)
            lbl = ''
            lbl2 = ''
            vcats = ''
            tagstring = ''
            plotstring = ''
            thumbnail = ''
            thumb2 = ''
            thumbslist = []
            length = ''
            lengthnum = ''
            vidid = ''
            vurl = ''
            views = ''
            vtitle = ''
            title = ''
            pubdate = ''
            reldate = ''
            SITE = ''
            if sitename is not None:
                if sitename == 'surfgay':
                    sitename = 'surfgayvideos'
                SITE = sitename
            else:
                sitename = ''
                SITE = ''            
            if vitem.has_key('video'):
                vid = vitem.get('video')
            else:
                vid = vitem
            if vid is not None:
                try:
                    assert isinstance(vid, dict)
                    if vid.has_key('url'):
                        vurl = vid.get('url')
                    elif vid.has_key('link'):
                        vurl = vid.get('link')
                    elif vid.has_key('embed'):
                        vurl = vid.get('embed')
                    if vurl.find('xtube') != -1 or vurl.find('spankwire') != -1:
                        SKIP = True
                    try:
                        if SITE is None or len(SITE)<1:
                            SITE = vurl.replace('http://', '').partition('/')[0].split('.', 1)[1].replace('.com', '').title()
                    except:
                        pass
                    SITE = sitename.lower()
                    if vid.has_key('default_thumb'):
                        thumbnail = vid.get('default_thumb')
                    elif vid.has_key('main_thumb'):
                        thumbnail = vid.get('main_thumb').replace(' ', '%20')
                    elif vid.has_key('thumbnail'):
                        if thumbnail == '':
                            thumbnail = vid.get('thumbnail')
                        else:
                            thumb2 = vid.get('thumbnail')
                    if vid.has_key('thumb'):
                        if thumbnail == '':
                            thumbnail = vid.get('thumb')
                        else:
                            thumb2 = vid.get('thumb')
                    if vid.has_key('views'):
                        views = vid.get('views')
                    if vid.has_key('duration'):
                        length = vid.get('duration')
                    if vid.has_key('length'):
                        length = vid.get('length')
                    elif vid.has_key('size'):
                        length = vid.get('size').get('seconds')
                    if vid.has_key('id'):
                        vidid = vid.get('id')
                    elif vid.has_key('video_id'):
                        vidid = vid.get('video_id')
                    else:
                        vidid = vurl.rsplit('-', 1)[0]
                    if vid.has_key('title'):
                        vtitle = vid.get('title').title().decode('utf-8', 'ignore') # .encode('ascii', 'ignore')
                    elif vitem.has_key('title'):
                        vtitle = vitem.get('title').title()
                    title = vtitle
                    if vid.has_key('publish_date'):
                        pubdate = vid.get('publish_date')
                    elif vitem.has_key('publish_date'):
                        pubdate = vitem.get('publish_date')
                    if len(pubdate) > 0:
                        reldate = pubdate
                        pubdate = pubdate.split(' ', 1)[0]
                    vtitle = vtitle.replace('"', '')
                    vtitle = vtitle.replace("'", '')
                    vtitle = vtitle.replace('*', '')
                    vtitle = vtitle.strip()
                    if len(vtitle) < 2:
                        vtitle = vurl.rpartition('/')[2]
                    lbl = vtitle.replace('&', 'and')
                    try:
                        if vid.has_key('category'):
                            vcats = vid.get('category')
                            plotstring = vcats
                        elif vid.has_key('categories'):  # and not SKIP:
                            vcatlist = vid.get('categories')
                            vcats = str(vcatlist[:]).replace("category':", "")
                            plotstring = vcats.replace("{", "").replace("}", "").replace("u'", "").replace("'", "").strip('[]')
                    except:
                        pass
                    try:
                        if vid.has_key("tags") and SITE.lower().find('motherless') == -1:  # and not SKIP:
                            tagslist = vid.get("tags")
                            tagstring = str(tagslist[:]).replace("tag_name':", "").replace("tag':", "").replace("{","").replace(
                                "}", "").replace("u'", "").replace("'", "").strip('[]')
                    except:
                        pass
                    if length == "00:00:00":
                        lengthnum = length
                        length = ''
                    elif len(length) > 0:
                        lengthnum = length
                        if length.find(':') == -1:
                            lenint = 0
                            seconds = int(length)
                            m, s = divmod(seconds, 60)
                            h, m = divmod(m, 60)
                            length = "%02d:%02d:%02d" % (h, m, s)
                            lengthnum = length
                    if vid.has_key('thumbs'):
                        thumbsdict = vid.get('thumbs')
                        if thumbsdict[0].has_key('src'):
                            for i in thumbsdict:
                                thumbslist.append(i.get('src'))
                            thumb2 = thumbslist[-1]
                    elif vitem.has_key('thumbs'):
                        if vitem.get('thumbs').has_key('big'):
                            thumbslist = vitem.get('thumbs').get('big')
                            thumb2 = thumbslist[-1]
                    lbl += ' {0} [COLOR yellow]{1}[/COLOR]\n[COLOR red]{2}[/COLOR]'.format(SITE, length, pubdate )
                except:
                    xbmc.log("*****ERROR MAKING VIDEO ITEM PARSING FIELDS LOOPING TO NEXT ITEMS\n---- {0}\n".format(str(vid)))
                #thumbnail = thumbnail.replace(' ', '%20')
                plotstring += "\n" + thumbnail + ' '
                lbl2 = "ID: {2} * Tags: {1} * {0}  ".format(plotstring, tagstring, vidid)                
                if len(vtitle) < 3:
                    vtitle = vurl.partition('.com')[0]
                    #vtitle = urllib2.unquote(vtitle).replace('http://', '').partition('.')[2]
                vpath = plugin.url_for(play, title=vtitle, video=thumbnail, url=vurl) #.encode('utf-8', 'ignore'))                
                #xli = ListItem(label=lbl, label2=lbl2, icon=thumbnail, thumbnail=thumbnail, path=vpath) #.encode('utf-8', 'ignore'))
                xli = ListItem(label=lbl, label2=lbl2, icon=thumbnail, thumbnail=thumbnail, path=vpath) #.encode('utf-8', 'ignore'))
                xli.thumbnail = thumbnail
                xli.icon = thumbnail
                xli.poster = vitem.get('main_thumb', 'DefaultVideo.png')
                #xli.set_art({'thumbnail': thumbnail, 'poster': thumbnail, 'icon': thumbnail})
                infolbl = {'Duration': lengthnum, 'Genre': SITE, 'Plot': plotstring + tagstring, 'Rating': views, 'Premiered': reldate, 'Year': reldate, 'Title': title}
                xli.set_info('video', info_labels=infolbl)
                #thumb2 = ''
                #if thumb2 != '':
                #    if len(thumbslist) > 0:
                #        xli.poster = thumbslist[0]
                #        xli.thumbnail = thumbslist[1]
                #        xli.icon = thumbslist[2]
                #        #xli.set_art({'fanart': thumbslist[-1]})
                #    else:
                #        xli.poster = thumb2
                        #xli.set_art({'fanart': thumb2})
                xli.playable = True
                litems.append(xli)
    except:
        xbmc.log("***LAST FAIL AFTER ALL ITEMS -- ERROR MAKINGVIDEOITEMS: {0}\n".format(vitem))
    if plugin.get_setting('sortresultsby') == 'date':
        litems.sort(key=lambda litems: litems.label)
    return litems


def parseVideosUrl(url):
    """
    Sends request to API and returns the JSON object as a List of Dicts which is parsed into XBMC ListItems by makeVideoItems
    :param url:
    :return: List(dict())
    """
    obj = dict()
    resp = None
    webresp = None
    if url.find('xtube.com') != -1 or url.find('motherless') != -1: obj = []
    headers = {}
    headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36'})
    headers.update({'Accept': 'application/json,text/x-json,text/x-javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8;charset=utf-8'})#;charset=utf8'})
    headers.update({'Accept-Language': 'en-US,en;q=0.5'})    
    # resp = urllib2.urlopen(req).read()
    try:
        try:
            req = urllib.request.Request(url, data=None, headers=headers)
            webresp = urlopen(req)
            resp = webresp.read()
        except:
            try:
                from urllib2 import Request
                req = Request(url, headers=headers)
                webresp = urllib2.urlopen(req)  
                resp = webresp.read()      
            except:
                pass
        obj = json.loads(resp.decode('latin', 'ignore'))
        assert isinstance(obj, dict)
        obj = clean_dict(obj)
        if url.find('xtube.com') != -1:
            tlist = []
            for i in obj.iterkeys(): tlist.append(obj.get(i))
            return tlist
    except:
        try:
            webresp = urlquick.get(url)  # download_page(url)
            obj = webresp.json()
        except:
            obj = None            
    try:
        newobj = []
        assert isinstance(obj, list)
        for ditem in obj:
            assert isinstance(ditem, dict)
            newobj.append(clean_dict(ditem))
        obj = newobj
    except:
        pass
    if url.find('xtube.com') != -1 or url.find('motherless') != -1: return obj
    try:
        if len(obj.keys()) == 1:
            return obj.get(obj.keys()[0])
        elif obj.has_key('videos'):
            return obj.get('videos')
        elif obj.has_key('data'):
            return obj.get('data')
        else:
            return obj
    except:
        xbmc.log("*** PARSE ERROR \n{0}".format(resp))
        return None


def readjson(filename='allcats.json'):
    dictallcats = dict()
    try:
        txt = file(path.join(__addondir__, 'resources', filename), 'r').read()
        dictallcats = json.loads(txt)  # dictallcats = json.JSONDecoder().decode(txt)
        if len(dictallcats.keys) == 1:
            return dictallcats.get(dictallcats.get(dictallcats.keys[0]))
        else:
            return dictallcats
    except:
        return []


def savejson(obj, filename):
    try:
        f = file(filename, 'w')
        txt = json.dump(obj, f)
        f.close()
    except:
        pass


def myvidster():
    url = ""
    resp = urlquick.get(url)
    src = resp.content
    html = src.rpartition('<ul class="slides clearfix">')[-1].split('<div class="pagination">',1)[0]
    matches = re.findall('href="(.+?)">(.+?)</a>', html)



def catlist_tube8(isGay=True):
    urlapi = "http://api.tube8.com/api.php?action=getcategorieslist&output=json"
    turl = getAPIURLS('tube8').replace('search=&', 'search={0}&')
    turl = turl.replace('search=gay&', 'search={0}+gay&')
    resp = ''
    litems = []
    allitems = []
    catlist = []
    resp = DL(urlapi)
    #resp = urllib2.urlopen(urlapi).read()
    obj = json.loads(unicode(resp).decode('latin', 'ignore'))
    try:
        if isGay:
            catlist = obj.get("gay")
        else:
            catlist = obj.get("straight")
        for catname in catlist:
            cname = catname.title()
            cimg = 'DefaultFolder.png'
            curl = turl.format(catname)
            cpath = plugin.url_for(site, sitename='tube8', section='index', url=curl)
            citem = dict(label=cname, icon=cimg, thumbnail=cimg, path=cpath)
            citem.setdefault(citem.keys()[0])
            allitems.append(citem)
        litems = sorted(allitems, key=lambda allitems: allitems['label'])
    except:
        pass
    return finish(litems)


def catlist_xtube():
    urlapi = "http://www.xtube.com/webmaster/api.php?action=getCategoryList"
    gturl = getAPIURLS('xtube')
    gturl = gturl.replace('&category=&', '&category={0}&')
    resp = ''
    html = ''
    catlist = []
    litems = []
    allitems = []
    resp = DL(urlapi)
    #resp = urllib2.urlopen(urlapi).read()
    obj = json.loads(unicode(resp).decode('latin', 'ignore'))
    try:
        assert isinstance(obj, list)
        for item in obj:
            assert isinstance(item, dict)
            catlist.append(item.values().pop())
        for catname in catlist:
            cimg = 'DefaultFolder.png'
            curl = gturl.format(urllib.quote_plus(catname))
            cpath = plugin.url_for(site, sitename='xtube', section='index', url=curl)
            citem = dict(label=catname.title(), icon=cimg, thumbnail=cimg, path=cpath)
            citem.setdefault(citem.keys()[0])
            allitems.append(citem)
        litems = sorted(allitems, key=lambda allitems: allitems['label'])
    except:
        pass
    return finish(litems)


def catlist_youporn():
    urlapi = "http://www.youporn.com/api/webmasters/categories/"
    gturl = getAPIURLS('youporn')
    gturl = gturl.replace('&category=&', '&category={0}&')
    resp = ''
    html = ''
    catlist = []
    litems = []
    allitems = []
    resp = DL(urlapi)
    #resp = urllib2.urlopen(urlapi).read()
    obj = json.loads(unicode(resp).decode('latin', 'ignore'))
    try:
        assert isinstance(obj, list)
        for item in obj:
            assert isinstance(item, dict)
            catlist.append(item.values().pop())
        for catname in catlist:
            # assert isinstance(catname, dict)
            # cname = catname.get('category')
            cimg = 'DefaultFolder.png'
            curl = gturl.format(urllib.quote_plus(catname))
            cpath = plugin.url_for(site, sitename='youporn', section='index', url=curl)
            citem = dict(label=catname.title(), icon=cimg, thumbnail=cimg, path=cpath)
            citem.setdefault(citem.keys()[0])
            allitems.append(citem)
        litems = sorted(allitems, key=lambda allitems: allitems['label'])
    except:
        pass
    return finish(litems)


def catlist_gaytube():
    # urlhtml = "http://www.gaytube.com/c/abc?m=azl"
    # Above is to try and scrape category pictures so defaultfolder doesn't have to be used but can't get a Regex to work
    urlapi = "http://www.gaytube.com/api/webmasters/categories/"
    gturl = getAPIURLS('gaytube').replace('&category=', '&category={0}')
    resp = ''
    html = ''
    catlist = []
    litems = []
    allitems = []
    resp = download_page(urlapi).decode('utf-8', 'ignore')
    obj = json.loads(resp)
    catlist = obj.get('categories')
    try:
        for catname in catlist:
            assert isinstance(catname, dict)
            cname = catname.get('category')
            cimg = 'DefaultFolder.png'
            curl = gturl.format(urllib.quote_plus(cname))
            cpath = plugin.url_for(site, sitename='gaytube', section='index', url=curl)
            citem = dict(label=cname.title(), icon=cimg, thumbnail=cimg, path=cpath)
            citem.setdefault(citem.keys()[0])
            allitems.append(citem)
        litems = sorted(allitems, key=lambda allitems: allitems['label'])
    except:
        pass
    return finish(litems)


def catlist_pornhub():
    urlapi = "http://www.pornhub.com/webmasters/categories"
    gturl = getAPIURLS('pornhub')
    ISGAY = True
    if gturl.find('=gay') != -1:
        gturl = gturl.replace('&category=gay&', '&category={0}&')
    else:
        ISGAY = False
        gturl = gturl.replace('&category=&', '&category={0}&')
    resp = ''
    html = ''
    catlist = []
    litems = []
    allitems = []
    resp = download_page(urlapi).decode('utf-8', 'ignore')
    obj = json.loads(resp)
    #resp = DL(urlapi)
    #resp = urllib2.urlopen(urlapi).read()
    #obj = json.loads(unicode(resp).decode('ascii'))
    catlist = obj.get('categories')
    try:
        for catname in catlist:
            assert isinstance(catname, dict)
            cname = catname.get('category')
            cimg = 'DefaultFolder.png'
            curl = gturl.format(urllib.quote_plus(cname))
            cpath = plugin.url_for(site, sitename='pornhub', section='index', url=curl)
            citem = dict(label=cname.title(), icon=cimg, thumbnail=cimg, path=cpath)
            citem.setdefault(citem.keys()[0])
            if ISGAY and cname.find('gay') != -1:
                allitems.append(citem)
            if not ISGAY and cname.find('gay') == -1:
                allitems.append(citem)
        litems = sorted(allitems, key=lambda allitems: allitems['label'])
    except:
        pass
    return finish(litems)


def catlist_redtube():
    urlapi = "http://api.redtube.com/?data=redtube.Categories.getCategoriesList&output=json"
    gturl = getAPIURLS('redtube').replace('&category=&', '&category={0}&')
    resp = ''
    html = ''
    catlist = []
    litems = []
    allitems = []
    resp = DL(urlapi)
    #resp = urllib2.urlopen(urlapi).read()
    obj = json.loads(unicode(resp).decode('ascii'))
    catlist = obj.get('categories')
    try:
        for catname in catlist:
            assert isinstance(catname, dict)
            cname = catname.get('category')
            cimg = 'DefaultFolder.png'
            curl = gturl.format(urllib.quote_plus(cname))
            cpath = plugin.url_for(site, sitename='redtube', section='index', url=curl)
            citem = dict(label=cname.title(), icon=cimg, thumbnail=cimg, path=cpath)
            citem.setdefault(citem.keys()[0])
            allitems.append(citem)
        litems = sorted(allitems, key=lambda allitems: allitems['label'])
    except:
        pass
    return finish(litems)


def groupslist_motherless():
    vitems = []
    litems = []
    allitems = []
    listofurls = groupurls_motherless()
    for url in listofurls:
        try:
            vitems = parseVideosUrl(url)
            litems = makeVideoItems(vitems)
            allitems.extend(litems)
        except:
            xbmc.log("Failed parsing URL {0}".format(url))
    allitems.sort(key=lambda allitems: allitems.label)
    return finish(allitems)


def groupurls_motherless():
    MOGROUPS2 = ['straight_men_having_fun_with_men', 'twinks', 'debbie_hearts_favorite_twinks', 'mmmmm_boys',
                 'selfshot_guys', 'boy_twink_ass', 'male_oral_sex_boys_18_', 'gay_incest', 'amateur_boys',
                 'naked_men_in_public', 'amateur_male_masturbation']
    MOGROUPS = ['amateur_boys', 'daddies___bros___bears_oh_my_', 'amateur_male_masturbation', 'naked_men_in_public',
                'twinks', 'debbie_hearts_favorite_twinks', 'straight_men_having_fun_with_men', 'men_gay_homosexuals',
                'real_hardcore_gay_group', 'selfshot_guys', 'boy_twink_ass', 'male_oral_sex_boys_18_',
                'nude_men_at_the_beach', 'gay_incest', 'father___son', '_gay_incest___family_fun_']
    burl = "http://motherless.com/feeds/groups/{0}/videos?page=1&format=json"
    # burl = str(getAPIURLS(sitename='motherless'))
    grouplist = []
    for grp in MOGROUPS:
        grouplist.append(burl.format(grp))
    return grouplist


def allcats_make():
    litems = []
    catlist = []
    allcatslist = []
    urltpl_list = []
    allitems = []
    caturls = getAPIURLS('CATEGORIES')
    DOSTR8 = plugin.get_setting(key='dostr8')
    if not (DOSTR8 == True or DOSTR8 == 'true'): DOSTR8 = False
    else: DOSTR8 = True
    for sitename, urlapi in caturls.items():
        resp = ''
        html = ''
        resp = DL(urlapi).decode('utf-8', 'ignore')
        obj = json.loads(resp)
        if isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict): catlist.append(item.values().pop())
        elif isinstance(obj, dict):
            if obj.has_key('categories'):
                catlist = obj.get('categories')
            elif obj.has_key('gay'):
                catlist = obj.get("gay")
            elif obj.has_key('straight'):
                catlist = obj.get("straight")
            if isinstance(catlist[0], dict):
                newcatlist = []
                for item in catlist: newcatlist.append(item.values().pop())
                catlist = newcatlist
        for catname in catlist:
            catname = catname.replace('-gay','')
            catname = catname.replace('&', ' ').replace('/',' ').replace('-', ' ')
            catname = catname.split(' ', 1)[0]
            catname = catname.lower()
            if not catname.endswith('s'): catnameplural = catname.lower()+'s'
            else: catnameplural = catname.lower()
            if catnameplural in allcatslist:
                pass
            elif catname in allcatslist:
                pass
            else:
                allcatslist.append(catname.lower())
    allcatslist.sort()
    allitems = []
    for catname in allcatslist:
        cimg = 'DefaultFolder.png'
        cimgname = catname.title().replace(' ', '').replace('&', '').replace('/','')
        cimg = __imgsearch__.replace('search.png', 'caticons/{0}.jpg'.format(cimgname))
        if not (path.exists(cimg) and path.isfile(cimg)):
            cimg = "http://cdn2.static.spankwire.com/images/category/Gay/{0}.jpg".format(cimgname)
            try:
                #resp = urllib2.urlopen(cimg)
                resp = DL(cimg)
                if resp.getcode() == 404: cimg = 'DefaultFolder.png'
            except:
                cimg = 'DefaultFolder.png'
        cpath = plugin.url_for(category, catname=catname.title())
        citem = dict(label=catname.title(), icon=cimg, thumbnail=cimg, path=cpath)
        citem.setdefault(citem.keys()[0])
        allitems.append(citem)
    savejson(allitems, __imgsearch__.replace('search.png', 'allcats.json'))
    return allitems


def getAPIURLS(sitename=None):
    """
    If a sitename is passes then just the URL to that sites API is returned if nothing is passed then a dictionary of Key=Sitename, Value=API URL is returned
    This function handles looking at the Plugin Settings to determine the Sorting/Ordering which defaults to NEWEST
    bugs still exist on ordering as dif API's use a dif word for other sortings but NEWEST works on all
    STR8 setting is checked and if it is enabled then the correct URL's are selected which doesn't specify segment=gay or gay in tags/search
    :param sitename:
    :return: URL of API for sitename specified or DICT(sitename: URL, sitename2: URL)
    """
    b = "http://www."
    a = "http://api."
    sitecatsapis = dict(spankwire=b+"spankwire.com/api/HubTrafficApiCall?data=getCategoriesList&output=json&segment=gay",
                        xtube=b+"xtube.com/webmaster/api.php?action=getCategoryList",
                        youporn=b+"youporn.com/api/webmasters/categories/",
                        gaytube=b+"gaytube.com/api/webmasters/categories/",
                        pornhub=b+"pornhub.com/webmasters/categories",
                        redtube=a+"redtube.com/?data=redtube.Categories.getCategoriesList&output=json",
                        tube8=a+"tube8.com/api.php?action=getcategorieslist&output=json")
    siteapis = dict(
        gaytube=b+"gaytube.com/api/webmasters/search/?ordering=newest&period=alltime&thumbsize=preview&category=&page=1&search=&tags[]=&count=250",
        pornhub=b+"pornhub.com/webmasters/search?id=44bc40f3bc04f65b7a35&category=gay&ordering=newest&tags[]=gay&search=&page=1&thumbsize=large",
        redtube=a+"redtube.com/?data=redtube.Videos.searchVideos&output=json&thumbsize=big&ordering=newest&page=1&search=&tags[]=gay&category=&period=alltime",
        spankwire=b+"spankwire.com/api/HubTrafficApiCall?data=searchVideos&output=json&ordering=newest&page=1&segment=gay&count=100&search=&tags=gay&thumbsize=big",
        tube8=a+"tube8.com/api.php?action=searchVideos&output=json&ordering=newest&search=gay&thumbsize=big&page=1&orientation=gay",
        xtube=b+"xtube.com/webmaster/api.php?action=getVideosBySearchParams&tags=&ordering=newest&thumbsize=400x300&fields=title,tags,duration,thumbnail,url,embed,categories&search=gay&category=&page=1&count=100",
        youporn=b+"youporn.com/api/webmasters/search?search=&page=1&ordering=newest&tags[]=gay&category=&thumbsize=big",
        motherless=b+"motherless.com/feeds/tags/gay/videos?format=json&limit=250&offset=0",
        motherless_search=b+"motherless.com/feeds/search/gay+{0}/videos?format=json&sort=date&offset=0&limit=250",
        porkytube=b+"porkytube.com/api/?output=json&command=media.newest&type=videos&offset=0&page=1&amount=500",
        porkytube_search=b+"porkytube.com/api/?output=json&command=media.search&q={0}&type=videos&offset=0&page=1&amount=500",
        surfgay=b+"surfgayvideo.com/api/?output=json&command=media.newest&type=videos&offset=0&page=1&amount=500",        
        surfgay_search=b+"surfgayvideo.com/api/?output=json&command=media.search&q={0}&type=videos&offset=0&page=1&amount=500")
        #porn5=b+'porn5.com/api/videos/find.json?cats=gay&limit=250&page=1&search=&order=date',
        #bonertube=b + 'bonertube.com/api/?output=json&command=media.newest&type=videos&offset=0&page=1&amount=500',
        #bonertube_search=b+'bonertube.com/api/?output=json&command=media.search&q={0}&type=videos&offset=0&page=1&amount=500')

    urls_straight = dict(
        gaytube=b + "gaytube.com/api/webmasters/search/?ordering=newest&period=alltime&thumbsize=all&count=100&page=1&search=&tags[]=",
        pornhub=b + "pornhub.com/webmasters/search?id=44bc40f3bc04f65b7a35&category=&ordering=newest&tags[]=&search=&page=1&thumbsize=medium",
        redtube=a + "redtube.com/?data=redtube.Videos.searchVideos&output=json&thumbsize=medium&ordering=newest&page=1&search=&tags[]=&category=&period=alltime",
        spankwire=b + "spankwire.com/api/HubTrafficApiCall?data=searchVideos&output=json&ordering=newest&page=1&segment=straight&count=100&search=&tags=&thumbsize=all",
        tube8=a + "tube8.com/api.php?action=searchVideos&output=json&ordering=newest&search=&thumbsize=big&page=1&orientation=straight",
        xtube=b + "xtube.com/webmaster/api.php?action=getVideosBySearchParams&tags=&ordering=newest&thumbsize=400x300&fields=title,tags,duration,thumbnail,url,embed,categories&search=&category=&page=1&count=100",
        youporn=b + "youporn.com/api/webmasters/search?search=&page=1&ordering=newest&tags[]=&category=&thumbsize=medium",
        motherless=b+"motherless.com/feeds/search/{0}/videos?format=json&offset=0&limit=250&sort=date")
    DOSTR8 = plugin.get_setting(key='dostr8')
    DOFILTER = plugin.get_setting(key='dofilter')
    if DOFILTER == 'true' or DOFILTER == True:
        DOFILTER = True
    else:
        DOFILTER = False
    MYTAGS = plugin.get_setting(key='tags').replace(',', '+')
    ORDERBY = plugin.get_setting(key='sortby')
    if DOSTR8 == True or DOSTR8 == 'true':
        DOSTR8 = True
        siteapis = urls_straight
        sitecatsapis.update(spankwire=b+"spankwire.com/api/HubTrafficApiCall?data=getCategoriesList&output=json&segment=straight")
    if ORDERBY != 'newest':
        urlstemp = siteapis
        tempdict = dict()
        for k, v in urlstemp.iteritems():
            url = v.replace('ordering=newest', 'ordering={0}'.format(ORDERBY))
            tempdict.update(k=url)
        siteapis = tempdict
    if DOFILTER and len(MYTAGS) > 0:
        urlstemp = siteapis
        tempdict = dict()
        if not DOSTR8:
            for k, v in urlstemp.iteritems():
                newurl = str(v).replace('&tags[]=gay&', '&tags[]=gay+{0}&'.format(MYTAGS))
                newurl = newurl.replace('&tags[]=&', '&tags[]={0}&'.format(MYTAGS))
                newurl = newurl.replace('&tags=&', '&tags={0}&'.format(MYTAGS))
                newurl = newurl.replace('&tags=gay&', '&tags=gay+{0}&'.format(MYTAGS))
                tempdict.update(k=newurl)
            siteapis.update(tempdict)
        else:
            for k, v in urlstemp.iteritems():
                newurl = str(v).replace('&tags[]=&', '&tags[]={0}&'.format(MYTAGS))
                newurl = newurl.replace('&tags=&', '&tags={0}&'.format(MYTAGS))
                tempdict.update(k=newurl)
            siteapis.update(tempdict)
    if sitename is None:
        return siteapis
    else:
        if sitename == 'CATEGORIES' or sitename == 'CATS':
            return sitecatsapis
        if siteapis.has_key(sitename):
            return siteapis.get(sitename)
        else:
            return siteapis


def find_video(url):
    matches = None
    vidurl = ''
    vidhtml = ''
    try:
        vidhtml = download_page(url).decode('utf-8', 'ignore')
        if url.find('youporn') != -1:
            matches = re.compile(ur'.(http://cdn.+?mp4.+?[^"])"', re.DOTALL + re.S + re.U).findall(vidhtml)
        elif url.find('porkytube') != -1:
            matches = re.compile(ur'href="(http://porkytube.com/media/videos/.+?)"', re.DOTALL + re.S + re.U).findall(vidhtml)
        elif url.find('bonertube') != -1:
            matches = re.compile(ur'.["\'](http://.+?mp4)["\'].', re.DOTALL + re.S + re.U).findall(vidhtml)
        elif url.find('tube8') != -1:
            matches = re.compile(ur'["\'](http://cdn.+?public.+?mp4.+?)["\']', re.DOTALL + re.S + re.U).findall(vidhtml)
        elif url.find('xtube') != -1:
            matches = re.compile(ur'"(http.+?mp4.+?[^"])"', re.DOTALL + re.S+re.U).findall(vidhtml)
        elif url.find('gaytube') != -1:
            matches = re.compile(ur'p="(http.+?mp4.+?[^"])"', re.DOTALL + re.S+re.U).findall(vidhtml)
        elif url.find('pornhub') != -1:
            matches = re.compile(ur'.(http.+?mp4.ipa=.+?[^\'])\'', re.DOTALL + re.S+re.U).findall(vidhtml)
        elif url.find('redtube') != -1:
            matches = re.compile(ur'="(http.+?mp4.+?[^"])"', re.DOTALL + re.S+re.U).findall(vidhtml)
        elif url.find('spankwire') != -1 or url.find('motherless') != -1:
            matches = re.compile(ur"'(http.+?mp4.+?[^'])'", re.DOTALL + re.S+re.U).findall(vidhtml)
    except:
        xbmc.log("\n****Failed to Resolve VID URL from REGEXes {0}\n{1}".format(url, str(repr(matches))))
    if matches is not None:
        vidurl = matches[0]
        vidurl = vidurl.replace('&amp;', '&')
        vidurl = vidurl.replace('http%3A%2F%2F', 'http://')
        vidurl = vidurl.replace('%2F','/')
        vidurl = vidurl.replace('%3F','?')
        vidurl = vidurl.replace('%3D', '=')
        if vidurl.startswith('http:\/\/'):
            vidurl = vidurl.replace('\/', '/')
        if vidurl.startswith('http:///'):
            urlparts = vidurl.split(':///')
            urlp2 = urlparts[1].replace('//', '/')
            vidurl = "http://{0}".format(urlp2)
        return vidurl
    else:
        return matches


@plugin.route('/tumblrhome')
def tumblrhome():
    blogname = 'gaypublicvideos'
    blogurlbase = "http://{0}.tumblr.com"
    blogs = plugin.get_setting('tumblrblog')
    bloglist = blogs.split('|')
    nowd = datetime.datetime.now()
    litems = []
    thre = re.compile(r'link rel=.+icon.+href="(http://68.media.tumblr.com/avatar_.+)"')
    titlere = re.compile(r'property="og:title" content="(.+[^"])" />')
    aboutre = re.compile(r'property="og:description" content="(.+[^"])" />')
    DEBUG = bool(plugin.get_setting('debugon'))
    if DEBUG:
        for blog in bloglist:
            path = plugin.url_for(endpoint=tumblr, blogname=blog, year=nowd.year.numerator, month=nowd.month.numerator, mostrecent=False)
            li = ListItem(label=blog, label2=blogurlbase.format(blog), icon='DefaultFolder.png', thumbnail='DefaultFolder.png', path=path)
            litems.append(li)
    else:
        if len(bloglist) > 100:
            bloglist = bloglist[0:100]
        for blog in bloglist:
            html = DL(blogurlbase.format(blog)).decode('utf-8')
            matchest = titlere.findall(html)
            matchesd = aboutre.findall(html)
            blogtitle = u''
            blogabout = u''
            bloglabel = blog.title()
            if len(matchest) > 0:
                blogtitle = matchest.pop().split('"',1)[0]
                if len(matchesd) > 0:
                    blogabout = matchesd.pop().split('"',1)[0]
                    if len(blogabout) > 22:
                        blogabout = blogabout[:22].strip() + ".."
                if HTML is not None:
                    blogtitle = HTML.unescape(blogtitle).title()
                    blogabout = HTML.unescape(blogabout).title()
                if len(blogtitle) < 2:
                    blogtitle = blog
                if blogtitle.lower().find('untitled') != -1:
                    blogtitle = blog
                bloglabel = blogtitle + "\n" + blogabout
            matches = thre.findall(html)
            blogthumb = 'DefaultFolder.png'
            if len(matches) > 0:
                blogthumb = matches.pop().split('"',1)[0]
            li = {'label': bloglabel, 'label2': blogabout, 'icon': blogthumb, 'thumbnail': blogthumb, 'path': plugin.url_for(endpoint=tumblr, blogname=blog, year=nowd.year.numerator, month=nowd.month.numerator, mostrecent=False)}
            li.setdefault(li.keys()[0])
            item = ListItem.from_dict(**li)
            item.set_info('video', {'genre': blog, 'year': blogabout})
            item.set_property('genre', blog)
            item.set_property('year', blogabout)
            litems.append(item)
    #plugin.add_items(items=litems)
    return finish(litems)


@plugin.route('/playtumblr/<url>')
def playtumblr(url):
    vidurl = None
    try:
        import YDStreamExtractor
        info = YDStreamExtractor.getVideoInfo(url, resolve_redirects=True)
        vidurl = info.streamURL()
    except:
        vidurl = url
    if vidurl is not None:
        #xbmc.Player().play(vidurl)
        plugin.set_resolved_url(vidurl)
        vitem = ListItem(label='Tumblr', label2=str(vidurl), icon='DefaultVideo.png', thumbnail='DefaultVideo', path=vidurl)
        vitem.set_info('video', {'Title': 'Tumblr {0}'.format(url), 'Plot': vidurl})
        vitem.set_is_playable(True)
        vitem.add_stream_info(stream_type='video', stream_values={})
        return vitem
    return None


def tumblrhtml(url, section="START CONTENT", sectionend="END CONTENT"):
    # section="Following"
    htmlbit = download_page(url).split('<!-- {0} -->'.format(section), 1)[-1]
    htmlbit = htmlbit.split('<!-- {0} -->'.format(sectionend), 1)[0]
    return htmlbit


def tumblrfollows():
    fre = re.compile(r'<a href="https://(.+)\.tumblr.com/".*?data-tumblelog-popover="(.*?)"', re.M)
    furl = "https://api.tumblr.com/v2/user/following"
    tumblrauth = { 'consumer_key': '5wEwFCF0rbiHXYZQQeQnNetuwZMmIyrUxIePLqUMcZlheVXwc4', 'consumer_secret': 'GCLMI2LnMZqO2b5QheRvUSYY51Ujk7nWG2sYroqozW06x4hWch', 'token': '7IuPrj2L6cfxMwOdbWV8yYYFafopwrYR3RYSdIc8YxMKJc8Dl5', 'token_secret': 'WSnl65etymR8m5KuK3rAX67emMCYzASpLrzIHQ2SKejYSqZmmh'}
    urlfollows = "https://api.tumblr.com/v2/user/following?limit=250"
    headers = {'Authorization': 'OAuth oauth_consumer_key = "5wEwFCF0rbiHXYZQQeQnNetuwZMmIyrUxIePLqUMcZlheVXwc4", oauth_nonce = "XiuBW4", oauth_signature = "N2hLobvUJd%2BK8OMZKr2YLlLC99M%3D", oauth_signature_method = "HMAC-SHA1", oauth_timestamp = "1485035014", oauth_token = "7IuPrj2L6cfxMwOdbWV8yYYFafopwrYR3RYSdIc8YxMKJc8Dl5", oauth_version = "1.0"'}
    #req = urllib2.Request(url=urlfollows, headers=headers)
    req = DL(urlfollows)


@plugin.route('/tumblr/<blogname>/<year>/<month>/<mostrecent>')
def tumblr(blogname, year, month, mostrecent):
    year = int(year)
    month = int(month)
    mostrecent = bool(mostrecent)
    fal = re.compile(r'class="post_thumb.+data-imageurl="(http://media.tumblr.com/tumblr.+frame1.jpg)".*?href="(http://.+tumblr.com/post/.+)".+data-peepr=".*?post_date">([^<]*)<', re.M+re.I)
    months = {v: k for k, v in enumerate(calendar.month_abbr)}
    blogurl = "http://{0}.tumblr.com".format(blogname)
    dateurl = blogurl + "/archive/{0}/{1}"
    recenturl = blogurl + "/archive/filter-by/video"
    vids = []
    lyear = ''
    lmonth = ''
    url = ''
    link = ''
    html = ''
    pubdate = ''
    numpages = 0
    nowd = datetime.datetime.now()
    if nowd.year == year and nowd.month == month:
        for monthnum in range(nowd.month, 0, -1):
            url = dateurl.format(nowd.year, monthnum)
            html += tumblrhtml(url)
            numpages += 1
        endmonth = numpages
        year = nowd.year - 1
        for monthnum in range(12, endmonth, -1):
            url = dateurl.format(year, monthnum)
            htmlbit = tumblrhtml(url)
            numpages += 1
            if len(htmlbit) > 0:
                html += htmlbit
            else:
                break
    else:
        for monthnum in range(int(month), 0, -1):
            url = dateurl.format(year, monthnum)
            html += tumblrhtml(url)
            numpages += 1
        endmonth = numpages
        year -= 1
        for monthnum in range(12, endmonth, -1):
            url = dateurl.format(year, monthnum)
            htmlbit = tumblrhtml(url)
            numpages += 1
            if len(htmlbit) > 0:
                html += htmlbit
            else:
                break
    matches = fal.findall(html) # list(set(fal.findall(html)))
    for thumbnail, url, dateof in matches:
        try:
            putdate = dateof.strip()
            monthstring, yearstr  = putdate.split(',', 1)
            lyear = int(x=yearstr.strip())
            lmonths, ldays = monthstring.strip().split(' ', 1)
            lday = int(x=ldays.strip())
            shortmonth = lmonths.strip()[0:3]
            lmonth = months.get(shortmonth.title())
            numberdate = datetime.date(lyear, lmonth, lday)
            itemname = url.rpartition('/')[-1]
            if itemname.isdigit(): itemname = blogname
            itemname = itemname.replace('-', ' ').title()
            #lbl2 = '{0} | {1}'.format(putdate, blogname)
            lbl = "{0}\n[COLOR yellow]({1})[/COLOR]".format(itemname, putdate)
            plugpath = plugin.url_for(playtumblr, url=url)
            li = {'label': lbl, 'label2': url, 'thumbnail': thumbnail, 'icon': thumbnail, 'path': plugpath, 'is_playable': True,'is_folder': False, 'info_type': 'video', 'info_labels': {}}
            li.setdefault(li.keys()[0])
            item = ListItem.from_dict(**li)
            vids.append(li)
        except:
            plugin.log.error("Failed to add item")
    imgnext = __imgsearch__.replace("search.", "next.")
    lbl = '-> Before {0} {1} ->'.format(month_abbr[lmonth], lyear)
    nextyear = lyear
    if lmonth > 1:
        nextmonth = lmonth - 1
    else:
        nextyear = nextyear - 1
        nextmonth = 12
    urlnext = plugin.url_for(endpoint=tumblr, blogname=blogname, year=int(nextyear), month=int(nextmonth), mostrecent=False)
    nextitem = {'label': lbl, 'label2': 'ZZZ next', 'thumbnail': imgnext, 'icon': imgnext, 'path': urlnext}
    nextitem.setdefault(nextitem.keys()[0])
    vids.append(nextitem)
    litems = []
    for item in vids:
        litem = ListItem.from_dict(**item)
        if litem.label2 != 'ZZZ next':
            litem.add_context_menu_items([('Download', 'RunPlugin("{0}")'.format(
                plugin.url_for(download, name=item.get('label'), url=item.get('label2'))),)])
        litems.append(litem)
    return finish(litems)


@plugin.route('/')
def index():
    """
    Index for plugin this just builds the main items for the site's linked to the SITEROOT destination
    :return: List of ListItems for Index of all sites
    """
    litems = []
    allitems = []
    viewmode = int(plugin.get_setting('viewmode'))
    if viewmode is None: viewmode = 500
    plugin.set_view_mode(viewmode)
    DOSTR8 = plugin.get_setting(key='dostr8')
    if not (DOSTR8 == True or DOSTR8 == 'true'): DOSTR8 = False
    else: DOSTR8 = True
    for sitename in getAPIURLS().keys():
        if sitename.find('_search') == -1:
            sicon = __imgsearch__.replace('search.', 'f{0}.'.format(sitename))
            spath = plugin.url_for(site, sitename=sitename, section='index', url='0')
            sitem = {'label': sitename.title(), 'icon': sicon, 'thumbnail': sicon, 'path': spath}
            sitem.setdefault(sitem.keys()[0])
            litems.append(sitem)
    allitems = sorted(litems, key=lambda litems: litems['label'])
    ifolder = __imgsearch__.replace('search.', 'folder.')
    itemallcats = {'label': 'Global Category List', 'path': plugin.url_for(allcats), 'icon': ifolder,
                  'thumbnail': ifolder}
    itemsearch = {'label': 'Search All Sites', 'path': plugin.url_for(search), 'icon': __imgsearch__,
                  'thumbnail': __imgsearch__}
    itemstream = {'label': 'Play Web URL', 'path': plugin.url_for(resolver), 'icon': 'DefaultFolder.png',
                  'thumbnail': 'DefaultFolder.png'}
    timg = __imgsearch__.replace('search.', 'ftumblr.')
    itemtumblr = {'label': 'Tumblr', 'icon': timg, 'thumbnail': timg, 'path': plugin.url_for(tumblrhome)}
    itemtumblr.setdefault(itemtumblr.keys()[0])
    itemallcats.setdefault(itemallcats.keys()[0])
    itemstream.setdefault(itemstream.keys()[0])
    itemsearch.setdefault(itemsearch.keys()[0])
    allitems.append(itemallcats)
    allitems.append(itemtumblr)    
    allitems.append(itemsearch)
    allitems.append(itemstream)
    return finish(allitems)


@plugin.route('/site/<sitename>/<section>/<url>/')
def site(sitename, section, url):
    """
    Main working function for the addon and handles Site specific calls to Search a site, Next Page, and Index.
    Index and Search sections call back into this section for Next Page support
    A shortcut helper SITEROOT simply calls this function for each site but looks up the correct URL to pass to section=Index
    :param sitename: Name of site to perform section actions on
    :param section: Index, Search, Next
    :param url: API URL for the section
    :return: Listitems for results plus a Search Site Item and Next Page Item
    """
    litems = []
    itemslist = []
    viewmode = int(plugin.get_setting('viewmode'))
    if viewmode is None: viewmode = 500
    plugin.set_view_mode(viewmode)
    DOSTR8 = plugin.get_setting(key='dostr8')
    __imgnext__ = __imgsearch__.replace('search.png', 'next.png')
    siteurl = getAPIURLS(sitename=sitename)
    if url == '0':
        url = siteurl
    pagenum = 2
    if siteurl.find('search=gay&') != -1:
        surl = siteurl.replace('search=gay&', 'search={0}+gay&')
    elif siteurl.find('porkytube') != -1 or siteurl.find('bonertube') != -1:
        surl = getAPIURLS(sitename='{0}_search'.format(sitename))
    elif siteurl.find('motherless') != -1:
        surl = siteurl
        surl = surl.replace('offset=1&','offset=0&')
        pagenum = 250
    else:
        surl = siteurl.replace('search=', 'search={0}')
    itemsearch = {'label': 'Search {0}'.format(sitename.title()),
                  'path': plugin.url_for(site, sitename=sitename, section='search', url=surl), 'icon': __imgsearch__,
                  'thumbnail': __imgsearch__}
    itemsearch.setdefault(itemsearch.keys()[0])
    pagestr = ''
    pagenumcur = pagenum - 1
    if url.find('page=') != -1 or url.find('offset=') != -1:
        if url.find('motherless') != -1:
            pagestr = str(url.split('offset=', 1)[1]).split('&', 1)[0]
        else:
            pagestr = str(url.split('page=', 1)[1]).split('&', 1)[0]
        if pagestr is not None:
            if url.find('motherless') != -1:
                pagenum = int(pagestr) + 250
            else:
                pagenum = int(pagestr) + 1
        else:
            if url.find('motherless') != -1:
                pagenum = 250
                pagenumcur = pagenum - 250
            else:
                pagenum = 2
    if url.find('page=1') != -1 or url.find('offset=0') != -1:
        if url.find('offset=0') != -1:
            nurl = url.replace('offset=0&', 'offset=250&')
        else:
            nurl = url.replace('page=1&', 'page=2&')
    elif url.find('page=') != -1 or url.find('offset=') != -1:
        if url.find('offset=') != -1:
            nurl = url.replace('offset={0}&'.format(pagenumcur), 'offset={0}&'.format(pagenum))
        else:
            nurl = url.replace('page={0}&'.format(pagenumcur), 'page={0}&'.format(pagenum))
    else:
        if url.find('offset=') == -1 and url.find('motherless') != -1:
            nurl = url + '&offset={0}'.format(pagenum)
        else:
            nurl = url + '&page={0}'.format(pagenum)
    mlabel = 'Next --> {0}'.format(pagenum)
    if url.find('motherless') != -1:
        mlabel = 'Next 250 to {0}'.format(pagenum+250)
    itemnext = {'label': mlabel, 'path': plugin.url_for(site, sitename=sitename, section='next', url=nurl), 'icon': __imgnext__, 'thumbnail': __imgnext__}
    itemnext.setdefault(itemnext.keys()[0])
    if section.lower() == "index":
        if sitename.lower() == "spankwire" and not (DOSTR8 == True or DOSTR8 == 'true'):
            isw = __imgsearch__.replace('search.', 'fspankwire.')
            item = {'label': 'Spankwire Gay Categories',
                    'path': plugin.url_for(site, sitename='spankwire', section='category', url=siteurl), 'icon': isw,
                    'thumbnail': isw}
            item.setdefault(item.keys()[0])
            litems = [item]
        elif sitename.lower() == "gaytube":
            igt = __imgsearch__.replace('search.', 'fgaytube.')
            item = {'label': 'GayTube Categories',
                    'path': plugin.url_for(site, sitename='gaytube', section='category', url=siteurl), 'icon': igt,
                    'thumbnail': igt}
            item.setdefault(item.keys()[0])
            litems = [item]
        elif sitename.lower() == "pornhub":
            igt = __imgsearch__.replace('search.', 'fpornhub.')
            item = {'label': 'PornHub Categories',
                    'path': plugin.url_for(site, sitename='pornhub', section='category', url=siteurl), 'icon': igt,
                    'thumbnail': igt}
            item.setdefault(item.keys()[0])
            litems = [item]
        elif sitename.lower() == "redtube":
            igt = __imgsearch__.replace('search.', 'fredtube.')
            item = {'label': 'RedTube Categories',
                    'path': plugin.url_for(site, sitename='redtube', section='category', url=siteurl), 'icon': igt,
                    'thumbnail': igt}
            item.setdefault(item.keys()[0])
            litems = [item]
        elif sitename.lower() == "xtube":
            igt = __imgsearch__.replace('search.', 'fxtube.')
            item = {'label': 'XTube Categories',
                    'path': plugin.url_for(site, sitename='xtube', section='category', url=siteurl), 'icon': igt,
                    'thumbnail': igt}
            item.setdefault(item.keys()[0])
            litems = [item]
        elif sitename.lower() == "tube8":
            igt = __imgsearch__.replace('search.', 'ftube8.')
            item = {'label': 'Tube8 Categories',
                    'path': plugin.url_for(site, sitename='tube8', section='category', url=siteurl), 'icon': igt,
                    'thumbnail': igt}
            item.setdefault(item.keys()[0])
            litems = [item]
        elif sitename.lower() == "youporn":
            igt = __imgsearch__.replace('search.', 'fyouporn.')
            item = {'label': 'YouPorn Categories',
                    'path': plugin.url_for(site, sitename='youporn', section='category', url=siteurl), 'icon': igt,
                    'thumbnail': igt}
            item.setdefault(item.keys()[0])
            litems = [item]
        if sitename.lower() == 'motherless':
            litems = groupslist_motherless()
            litems.insert(0, itemsearch)
            litems.append(itemnext)
        else:
            # Index was called so get the first page of a specific site and return items with a Search and Next added
            vitems = [itemsearch]
            if len(litems) > 0:
                vitems = [litems[0],itemsearch]
            itemslist = parseVideosUrl(url)
            litems = makeVideoItems(itemslist)
            itemslist = litems
            itemslist.append(itemnext)
            vitems.extend(itemslist)
            litems = vitems
    elif section.lower() == "next":
        # Provides support for viewing Next set of results/page and accessed from the itemnext ListItem added to Index/Search
        vitems = list()
        itemslist = parseVideosUrl(url)
        litems = makeVideoItems(itemslist)
        itemslist = litems
        itemslist.insert(0, itemsearch)
        itemslist.append(itemnext)
        litems = itemslist
    elif section.lower() == "category":
        if sitename.lower() == 'spankwire':
            txt = file(path.join(__addondir__, 'spankwire.json')).read()
            allitems = json.loads(txt)
            itemlist = allitems.get(allitems.keys()[0])
            allitems = sorted(itemlist, key=lambda itemlist: itemlist['label'])
            for li in allitems:
                assert isinstance(li, dict)
                catpath = plugin.url_for(site, sitename='spankwire', section='index', url=li.get('path'))
                li.update(path=catpath)
                li.setdefault(li.keys()[0])
                litems.append(li)
        elif sitename.lower() == 'gaytube':
            litems = catlist_gaytube()
        elif sitename.lower() == 'pornhub':
            litems = catlist_pornhub()
        elif sitename.lower() == 'redtube':
            litems = catlist_redtube()
        elif sitename.lower() == 'xtube':
            litems = catlist_xtube()
        elif sitename.lower() == 'youporn':
            litems = catlist_youporn()
        elif sitename.lower() == 'tube8':
            if not (DOSTR8 == True or DOSTR8 == 'true'):
                litems = catlist_tube8(isGay=True)
            else:
                litems = catlist_tube8(isGay=False)
    elif section.lower() == "search":
        # Perform a search of the specific site and return results and a next page item - NOT a global multisite search
        searchtxt = ''
        try:
            searchtxt = plugin.get_setting('lastsearch')
        except:
            searchtxt = ''
        searchtxt = plugin.keyboard(searchtxt, 'Search {0}'.format(sitename.title()), False)
        searchquery = searchtxt.replace(' ', '+')
        plugin.set_setting(key='lastsearch', val=searchtxt)
        mlabel = 'Next {0} --> {1}'.format(searchtxt, pagenum)
        surl = surl.format(searchquery)
        if url.find('motherless') != -1:
            nurl = surl.replace('offset=0&', 'offset=250&')
            mlabel = 'Next {0} --> {1}'.format(searchtxt, str(pagenum+250))
        else:
            nurl = surl.replace('page=1&', 'page=2&')
        itemslist = parseVideosUrl(surl)
        litems = makeVideoItems(itemslist)
        itemslist = litems
        itemslist.insert(0, itemsearch)
        itemnext = {'label': mlabel, 'path': plugin.url_for(site, sitename=sitename, section='next', url=nurl),
                    'icon': __imgnext__, 'thumbnail': __imgnext__}
        itemnext.setdefault(itemnext.keys()[0])
        itemslist.append(itemnext)
        litems = itemslist
    #return plugin.finish(items=litems)
    #return plugin.finish(items=litems, sort_methods=[SortMethod.LABEL, SortMethod.GENRE, SortMethod.DURATION, SortMethod.VIDEO_YEAR, SortMethod.VIDEO_RATING])
    return finish(litems)


@plugin.route('/gaypower/<page>')
def gaypower(page=1):
    viewmode = int(plugin.get_setting('viewmode'))
    if viewmode is None: viewmode = 500
    plugin.set_view_mode(viewmode)
    boardurl = 'http://gaypower.org/index.php?page=Board&boardID=59&pageNo=' + page
    threadurl = 'http://gaypower.org/index.php?page=Thread&postID={0}'
    __imgnext__ = __imgsearch__.replace('search.png', 'next.png')
    page = int(page) + 1
    npath = plugin.url_for(gaypower, page=page)
    itemnext = {'label': 'Next --> {0}'.format(page), 'path': npath, 'icon': __imgnext__, 'thumbnail': __imgnext__}
    itemnext.setdefault(itemnext.keys()[0])
    bhtml = ''
    for p in range(1, 4):
        boardurl = "http://gaypower.org/index.php?page=Board&boardID=59&pageNo={0}".format(p)
        bhtml += DL(boardurl)
        #bhtml += urllib2.urlopen(boardurl).read()
    # bhtml = urllib2.urlopen(boardurl).read()
    recol = 'class="columnTopic" title="(.+?)".+?<a href="(.+?)">(.+?)</a>'
    reflashx = re.compile('(http://www.flashx.tv\/[^\"\s]*).')
    rethumb = re.compile('(http.+jpg)[\s\S]')
    vids = re.compile(recol, re.S).findall(bhtml)
    litems = []
    allitems = []
    thumb = 'DefaultVideo.png'
    if len(vids) > 0:
        try:
            for img, link, title in vids:
                if img.find('flashx.tv') != -1:
                    vurl = reflashx.findall(img)
                    imgmatch = rethumb.findall(img)
                    if len(imgmatch) > 0:
                        thumb = imgmatch.pop()
                    if thumb.find('.jpg') == -1 and thumb.find('.png') == -1:
                        thumb = 'DefaultVideo.png'
                    if len(vurl) > 0:
                        try:
                            vidurl = str(vurl[0])
                            vidurlorig = vidurl.encode('utf-8')
                            vidurl = vidurl.replace('/embed-', '/')
                            if vidurl.find('.html') != -1:
                                vidurl = vidurl.replace('.html', '.htm')
                            if vidurl.find('-') != -1:
                                vidurl = vidurl[0:vidurl.find('-')]
                            if vidurl.find('.htm') == -1:
                                vidurl = vidurl + '.htm'
                            vtitle = "{0} (GayPower.org - flashx)".format(str(title).title())
                            vpath = plugin.url_for(play, title=vtitle, video=thumb, url=vidurl.encode('utf-8'))
                            vpath2 = plugin.url_for(playmovie, url=vidurl)
                            item = ListItem(label=title, icon=thumb, thumbnail=thumb, path=vpath2)
                            item.set_info(info_type='video', info_labels={"Plot": vidurl})
                            item.playable = True
                            item.thumbnail = thumb
                            item.icon = thumb
                            item.add_context_menu_items([('Download', 'RunPlugin("{0}")'.format(
                                plugin.url_for(download, name=title, url=vidurl)),)])
                            allitems.append(item)
                        except:
                            xbmc.log("Error Resolving URL for Flashx ListItem")
            litems = sorted(allitems, key=lambda allitems: allitems.label)
            # litems = sorted(allitems, key=lambda allitems: allitems['label'])
        except:
            xbmc.log("Problem converting page to listitems")
    # litems.append(itemnext)
    # No Next page as only 4 pages of results so I load them all at the same time and sort them and list them
    #return plugin.finish(items=litems, sort_methods=[SortMethod.LABEL_IGNORE_THE, SortMethod.GENRE, SortMethod.DURATION, SortMethod.VIDEO_YEAR, SortMethod.VIDEO_RATING])
    #return plugin.finish(items=litems)
    return finish(litems)


@plugin.route('/resolver')
def resolver():
    litems = []
    url = ''
    cimg = 'DefaultVideo.png'
    try:
        url = plugin.keyboard(default='', heading='Video Page URL')
        if url != "":
            return playmovie(url)
            #plugin.redirect(plugin.url_for(playmovie, url=url))
        else:
            #plugin.redirect(plugin.url_for(index))
            return None
    except:
        pass
    #plugin.redirect(plugin.url_for(index))
    #return plugin.finish()
    #return []


@plugin.route('/allcats')
def allcats():
    rawjson = file(__imgsearch__.replace('search.png', 'allcats.json')).read().decode('utf-8', 'ignore')
    rawjson = rawjson.replace('"thumb":', '"thumbnail":')
    catlist = json.loads(rawjson)
    for item in catlist:
        item.setdefault(item.keys()[0])
    return finish(catlist)
    #return plugin.finish(items=catlist, succeeded=True, cache_to_disc=True)


@plugin.route('/category/<catname>')
def category(catname):
    url_list = []
    gturl = ''
    litems = []
    allitems = []
    catname = catname.lower().decode('utf-8', 'ignore')
    listofsites = getAPIURLS('CATEGORIES')
    apiurl = getAPIURLS('motherless_search')
    try:
        itemlist = parseVideosUrl(apiurl.format(catname))
        litems = makeVideoItems(itemlist, 'motherless')
    except:
        plugin.log.error('***ERROR MAKING MOTHERLESS CATEGORY VIDS')
        litems = []
    apiurl = getAPIURLS('porkytube_search').format(catname)
    try:
        itemlist = parseVideosUrl(apiurl)
        litems.extend(makeVideoItems(itemlist, 'porkytube'))
    except:
        plugin.log.error('***ERROR MAKING PORKYTUBE CATEGORY VIDS')
    for sitename in listofsites.keys():
        try:
            if sitename == 'motherless':
                apiurl = getAPIURLS('motherless_search')
            else:
                apiurl = getAPIURLS(sitename)
            gturl = apiurl.replace('&category=&', '&category={0}&')
            if sitename == 'redtube':
                gturl = gturl.replace('&tags[]=&', '&tags[]={0}&')
            if sitename == 'youporn':
                gturl = gturl.replace('&search=&','&search={0}&')
            if sitename == 'spankwire':
                gturl = gturl.replace('&search=&','&search={0}&')
            if sitename == 'xtube':
                gturl = gturl.replace('&tags=&','&tags={0}&')
            if sitename == 'tube8':
                gturl = gturl.replace('search=&', 'search={0}&')
                gturl = gturl.replace('search=gay&', 'search={0}&')
            if sitename == 'pornhub' and gturl.find('category=gay') != -1:
                gturl = gturl.replace('category=gay&', 'category={0}-gay&')
            surl = gturl.format(urllib.quote_plus(catname))
            itemlist = parseVideosUrl(surl)
            allitems = makeVideoItems(itemlist, sitename=sitename)
            litems.extend(allitems)
        except:
            plugin.log.error('***ERROR MAKING ITEMS FOR {0}'.format(sitename))
    litems.sort(key=lambda litems : litems.label)
    #return plugin.finish(items=litems, sort_methods=[SortMethod.LABEL_IGNORE_THE, SortMethod.GENRE, SortMethod.VIDEO_RUNTIME, SortMethod.VIDEO_YEAR, SortMethod.VIDEO_RATING])
    return finish(litems)


@plugin.route('/search')
def search():
    """
    Pop's up a keyboard with the default value read from settings with whatever was typed last time.
    Loops over the list of JSON API's putting the search word into the URL and making ListItems for each site before
    combining all results and sorting them
    """
    viewmode = int(plugin.get_setting('viewmode'))
    if viewmode is None: viewmode = 500
    plugin.set_view_mode(viewmode)
    searchtxt = ''
    searchtxt = plugin.get_setting('lastsearch')
    searchtxt = plugin.keyboard(searchtxt, 'Search All Sites', False)
    searchquery = searchtxt.replace(' ', '+')
    plugin.set_setting(key='lastsearch', val=searchtxt)
    litems = []
    allitems = []
    itemslist = []
    DOSTR8 = plugin.get_setting(key='dostr8')
    __imgnext__ = __imgsearch__.replace('search.png', 'next.png')
    siteurls = getAPIURLS()
    siteurls.pop('motherless')
    siteurls.pop('motherless_search')
    siteurls.pop('porkytube')
    for k, v in siteurls.iteritems():
        siteurl = v
        sitelabel = k
        if sitelabel.find("_search") != -1: sitelabel = sitelabel.replace('_search', '')
        surl = siteurl
        if siteurl.find('{0}') == -1:
            if siteurl.find('search=gay&') != -1:
                surl = siteurl.replace('search=gay&', 'search={0}+gay&')
            else:
                surl = siteurl.replace('search=', 'search={0}')
        searchurl = surl.format(searchquery)
        itemslist = parseVideosUrl(searchurl)
        allitems.extend(makeVideoItems(itemslist, sitename=sitelabel))

    murl = 'http://motherless.com/feeds/search/gay+{0}/videos?format=json&sort=date&offset=0&limit=250'
    if searchtxt.find("-gay") != -1:
        murl = 'http://motherless.com/feeds/search/{0}/videos?format=json&sort=date&offset=0&limit=250'
        searchtxt = searchtxt.replace('-gay','')
        searchquery = urllib.quote_plus(searchtxt)
    murl = murl.format(searchquery)
    try:
        itemslist = parseVideosUrl(murl)
        allitems.extend(makeVideoItems(itemslist, sitename='motherless'))
    except:
        xbmc.log("***ERROR GETTING MOTHERLESS SEARCH RESULTS***\n{0}".format(murl))
    litems = allitems
    litems.sort(key=lambda litems: litems.label) #= sorted(allitems, key=lambda allitems: allitems.label)
    #plugin.set_content('movies')
    #return plugin.finish(items=litems, sort_methods=[SortMethod.LABEL_IGNORE_THE, SortMethod.GENRE, SortMethod.DURATION, SortMethod.VIDEO_YEAR, SortMethod.VIDEO_RATING])
    return finish(litems)


@plugin.route('/playmovie/<url>')
def playmovie(url):
    resolved = ''
    stream_url = ''
    item = None
    try:
        import urlresolver
        resolved = urlresolver.HostedMediaFile(url).resolve()
        if not resolved or resolved == False or len(resolved) < 1:
            resolved = urlresolver.resolve(url)
            if resolved is None or len(resolved) < 1:
                resolved = urlresolver.resolve(urllib.unquote(url))
        if len(resolved) > 1:
            plugin.notify(msg="PLAY {0}".format(resolved.split('.',1)[-1]), title="URLRESOLVER {0}".format(url.split('.',1)[-1]), delay=2000)
            plugin.set_resolved_url(resolved)
            item = ListItem.from_dict(path=resolved)
            item.add_stream_info('video', stream_values={})
            item.set_is_playable(True)
            return item
    except:
        resolved = ''
        plugin.notify(msg="URLResolver Failed {0}".format(resolved.split('.',1)[-1]), title="Trying..YOUTUBE-DL {0}".format(url.split('.',1)[-1]), delay=2000)
    try:
        import YDStreamExtractor
        info = YDStreamExtractor.getVideoInfo(url, resolve_redirects=True)
        resolved = info.streamURL()
        for s in info.streams():
            try:
                stream_url = s['xbmc_url'].encode('utf-8', 'ignore')
                xbmc.log(msg="**YOUTUBE-DL Stream found: {0}".format(stream_url))
            except:
                pass
        if len(stream_url) > 1:
            resolved = stream_url
        if len(resolved) > 1:
            plugin.notify(msg="PLAY {0}".format(resolved.split('.',1)[-1]), title="YOUTUBE-DL {0}".format(url.split('.',1)[-1]), delay=2000)
            plugin.set_resolved_url(resolved)
            item = ListItem.from_dict(path=resolved)
            item.add_stream_info('video', stream_values={})
            item.set_is_playable(True)
            return item
    except:
        plugin.notify(msg="YOUTUBE-DL Failed: {0}".format(resolved.split('.',1)[-1]), title="Can't play {0}".format(url.split('.',1)[-1]), delay=2000)

    if len(resolved) > 1:
        plugin.set_resolved_url(resolved)
        item = ListItem.from_dict(path=resolved)
    else:
        plugin.set_resolved_url(url)
        plugurl = 'plugin://plugin.video.live.streamspro/?url={0}'.format(urllib.quote_plus(url))
        item = ListItem.from_dict(path=plugurl)
    item.add_stream_info('video', stream_values={})
    item.set_is_playable(True)
    plugin.notify(msg="RESOLVE FAIL: {0}".format(url.split('.',1)[-1]), title="Trying {0}".format(item.path.split('.',1)[-1]), delay=2000)
    return item


#@plugin.route('/playmovie/<url>')
def playmovie_old(url):
    try:
        import urlresolver
        resolved = ''
        mid = url.rpartition('/')[2]
        mid = mid.split('.',1)[0]
        if mid.find('embed') != -1: mid = mid.replace('embed-', '')
        if mid.find('-') != -1: mid = mid.rpartition('-')[0]
        host = None
        try:
            resolved = urlresolver.HostedMediaFile(url).resolve()
            if not resolved:
                resolved = urlresolver.resolve(url)
                #resolved = urlresolver.HostedMediaFile("http://www.flashx.tv/embed.php?c={0}".format(mid)).resolve()
                if resolved is None or len(resolved) < 1:
                    resolved = urlresolver.resolve(urllib.unquote(url))
                    #resolved = urlresolver.resolve("http://www.flashx.tv/{0}.html".format(mid))
                #if resolved is None or resolved == False or len(resolved) < 1:
                #    resolved = urlresolver.resolve("http://www.flashx.tv/{0}.htm".format(mid))
                #if resolved is None or resolved == False or len(resolved) < 1:
            if not resolved or len(resolved) < 1:
                try:
                    import YDStreamExtractor
                    info = YDStreamExtractor.getVideoInfo(url, resolve_redirects=True)
                    resolved = info.streamURL()
                    return [plugin.play_video(resolved)]
                except:
                    pass
        except:
            xbmc.log("\n****Resolve attempts all failed Failed to use URL Resolver to play video {0}".format(url))
        vli = ListItem(label='Gaypower', label2=url, path=resolved.encode('utf-8'))
        vli.playable = True
        vli.thumbnail = 'DefaultVideo.png'
        vli.icon = 'DefaultVideo.png'
        #xbmc.log("\n****URL RESOLVER RESULT = {0}".format(str(repr(vli))))
        #plugin.play_video(vli)
        xbmc.executebuiltin('PlayMedia(%s)' % resolved.decode('utf-8', 'ignore'))
        # return plugin.end_of_directory()
    except:
        resolved = find_video(url)
        if resolved is not None:
            plugin.play_video(resolved)
            xbmc.executebuiltin('PlayMedia(%s)' % resolved.decode('utf-8', 'ignore'))
        else:
            try:
                livestreamerurl = 'plugin://plugin.video.livestreamerkodi/play/{0}'.format(urllib.quote_plus(url))
                xbmc.executebuiltin('RunPlugin({0})'.format(livestreamerurl))
            except:
                xbmc.log("\n****Failed to use URL Resolver to play video {0}".format(url))


@plugin.route('/play/<url>/<video>/<title>')
def play(url='', video='DefaultVideo.png', title=''):
    if len(title) < 1:
        title = str(url.partition('.com')[0])
        title = urllib.unquote(title).replace('http://','').partition('.')[2]
    vidurl = ''
    vli = None
    try:
        vidurl = find_video(url)
        if vidurl is not None:
            plugin.set_resolved_url(vidurl)
            vli = ListItem.from_dict(label=title, label2="{0} / {1}".format(url, vidurl), thumbnail=video, path=vidurl)
            vli.set_is_playable(True)
            vli.add_stream_info(stream_type='video', stream_values={})
            return vli
    except:
        plugin.notify(msg="FAILED: {0} no video found on {1}".format(title, url.split('.',1)[-1]), title="Trying Resolvers for {0}".format(url))
    return playmovie(url)


def play_old(url='', video='DefaultVideo.png', title=''):
    """
    Play attempts to scrape the video's page and find the actual video file to play. This is still buggy but seems to work on
    a lot of the sites but not all the time so any help on this function working better would be appreciated. I pass in the
    title of the movie and the video tags the Thumbnail which I use to create a proper ListItem with the scrapped MP4 url
    :param title: Video Title to play passed to XBMC in a new ListItem object with resolved URL of video scraped from url
    :param video: Thumbnail URL of the video used as the icon and thumbnail for ListItem to play
    :param url: URL of the embed/video page to scrape for the real playable video file
    :return: ListItem of video with path = scraped url of the MP4/Video file hopefully
    """
    if len(title) < 1:
        title = str(url.partition('.com')[0])
        title = urllib.unquote(title).replace('http://','').partition('.')[2]
        #title = urllib2.unquote(
    resolved = None
    mediaurl = None
    vidhtml = ''
    vidurl = ''
    vli = None
    try:
        vidurl = find_video(url)
        if vidurl is not None:
            #plugin.play_video(vidurl.decode('utf-8', 'ignore'))
            xbmc.executebuiltin('PlayMedia(%s)' % vidurl.decode('utf-8', 'ignore'))
            #plugin.clear_added_items()
            #return plugin.finish(items=[plugin.set_resolved_url(vidurl)], succeeded=True, update_listing=False, cache_to_disc=False)
            #return []
            #plugin.play_video(vidurl)
    except:
        xbmc.log("\n***FLASHVAR SCRAPE FAILED TO PLAY SCRAPED SOURCE {0}".format(url))
    try:
        if vidurl is None:
            livestreamerurl = 'plugin://plugin.video.livestreamerkodi/play/{0}'.format(urllib.quote_plus(url))
            #plugin.play_video(url)
            xbmc.executebuiltin('RunPlugin({0})'.format(livestreamerurl))
    except:
        livestreamerurl = 'plugin://plugin.video.livestreamer/play/?url={0}'.format(urllib.quote_plus(url))
        xbmc.executebuiltin('RunPlugin({0})'.format(livestreamerurl))
        #plugin.set_resolved_url(url)
    # plugin.set_resolved_url(url)
    # plugin.clear_added_items()
    # return plugin.finish(items=None, update_listing=True, cache_to_disc=False)
    # return plugin.end_of_directory(True, True, False)
    #return plugin.finish()


@plugin.route('/download/<name>/<url>')
def download(name='', url=''):
    resolved = None
    hosturl = url[url.find('://') + 3:url.find('.com/')]  # .split('/',1)[0]
    if not hosturl in getAPIURLS().keys():
        try:
            import urlresolver
            host = urlresolver.HostedMediaFile(url)
            if host:
                resolver = urlresolver.resolve(url)
                resolved = resolver
        except:
            pass
    else:
        try:
            resolved = find_video(url)
        except:
            pass
    try:
        import YDStreamExtractor
        if resolved is None:
            info = YDStreamExtractor.getVideoInfo(url, resolve_redirects=True)
            resolved = info.streamURL()
            if resolved is not None:
                if resolved.find('|') != -1: resolved = resolved.partition('|')[0]
            else:
                xbmc.log("\n*****Failed to resolve URL to downloadable video {0}".format(url))
                return None
        savepath = ''
        savepath = plugin.get_setting('downloadpath')
        info = YDStreamExtractor.getVideoInfo(resolved, resolve_redirects=True)
        if savepath == '':
            result = YDStreamExtractor.handleDownload(info, bg=True)
        else:
            result = YDStreamExtractor.handleDownload(info, bg=True, path=savepath)
        plugin.notify(title="DOWNLOADED {0} from {1}".format(url, resolved), msg="{0}".format(str(repr(result))))
        xbmc.log("\n***DOWNLOAD {0} from {1}\n***RESULT {2}\n".format(url, resolved, str(repr(result))))
    except:
        plugin.notify(msg="ERROR downloading {0}".format(url), title="Couldn't Download")
    #return plugin.finish(items=[])
    return None


@plugin.route('/setViewMode')
def setView():
    try:
        import xbmcutil
        import xbmcutil.viewModes as viewModes
        viewModes.Selector('video')
    except:
        try:
            from viewModes import Selector
            view = Selector('video')
            plugin.notify(msg="View {0}".format(view.currentMode))
        except:
            pass
    return None


def finish(items=[]):
    plugin.set_content('movies')
    #for sort in lstSorts: plugin.add_sort_method(sort_method=sort)
    viewmode = int(plugin.get_setting('viewmode'))
    if viewmode is None:
        viewmode = 500
        plugin.set_setting('viewmode', viewmode)
    xlitems = []
    for item in items:
        if not isinstance(item, ListItem):
            li = ListItem.from_dict(**item)
        else:
            li = item
        if str(li.path).find('playmovie') != -1 or urllib.unquote_plus(li.path).find('/play') != -1:
            itemurl = li.path.rpartition('/playmovie/')[0]
            pathdl = plugin.url_for(endpoint=download, name=li.label, url=itemurl)
            li.add_context_menu_items([('Download', 'RunPlugin({0}'.format(pathdl)),])
            li.set_is_playable(True)
            li.set_info(type='video', info_labels={'Title': li.label, 'Plot': li.label2})
            li.add_stream_info(stream_type='video', stream_values={})
        xlitems.append(li)
    return xlitems


if __name__ == '__main__':
    try:
        import xbmcutil
        if xbmcutil.plugin.actions[0] == u"setviewmode":
            #from xbmcutil import viewModes
            import xbmcutil.viewModes as viewModes
            viewModes.Selector('video')
    except:
        pass
    plugin.run()
