# -*- coding: utf8 -*-
import urllib2
import urllib
import cookielib
import string
import json
import os
import time

#I am not able to use re which XXX me.

def cancelHTML(content):
    place1 = content.find("<")
    place2 = content.find(">")
    while place1 > -1:
        content = content[:place1] + content[place2+1:]
        place1 = content.find("<")
        place2 = content.find(">")
    return content

def parseID(url, key):
    place1 = url.find(key)
    place2 = url.find("&", place1)
    return url[place1+len(key):place2]

class renren:
    def __init__(self, email, password):
        self.email = email
        self.__pw = password
        self.__rtk = ""
        self.__id = ""
        self.__name = ""
        self.__cj = cookielib.MozillaCookieJar()
        self.__mid = 1
        
    def __relogin(self):
        postdata=urllib.urlencode({'email':self.email, 'password':self.__pw, 'origURL':'http://www.renren.com/Home.do', 'domain':'renren.com', 'key_id': '1', 'autoLogin':'True'})
        req = urllib2.Request(url = 'http://www.renren.com/ajaxLogin/login', data = postdata)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.802.30 Safari/535.1 SE 2.X MetaSr 1.0')#添加浏览器信息（可以无视）
        content = urllib2.urlopen(req)
        response = urllib2.urlopen('http://www.renren.com')
        print "relogin"
        self.__cj.save(self.email, ignore_discard=True, ignore_expires=True)        
    def login(self):
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cj))
        urllib2.install_opener(opener)
        if os.path.exists(self.email):
            self.__cj.load(self.email, True, True)
            content = urllib2.urlopen("http://notify.renren.com/wpi/getonlinecount.do").read()
            if ("verify failure" in content) or (content == ""):
                self.__relogin()
        else:
            self.__relogin()
        content = urllib2.urlopen("http://notify.renren.com/wpi/getonlinecount.do").read()
        if ("verify failure" in content) or (content == ""):
            return False
        jsonList = json.loads(content)
        self.__id = str(jsonList["hostid"])
        self.__name = jsonList["hostname"]
        content = urllib2.urlopen("http://www.renren.com").read()
        place = content.find("_rtk :")
        self.__rtk = content[place+8: place+17].replace("\'", "").replace(",", "")
        urllib2.urlopen("http://wpi.renren.com/comet_get?mid=0&ins")
        return True
    def showContent(self, url = "http://www.renren.com"):
        content = urllib2.urlopen(url).read()
        return content
    def islogin(self):
        content = urllib2.urlopen("http://notify.renren.com/wpi/getonlinecount.do").read()
        if ("verify failure" in content) or (content == ""):
            return False
        return True
    def makefans(self, pageid):
        url = "http://page.renren.com/makefans"
        postdata = "pid=" + str(pageid) + "&_rtk=" + self.__rtk
        content = urllib2.urlopen(url = url, data = postdata).read()
        return content
    def getInformation(self):
        return(self.email, self.__id, self.__name, self.__rtk)
    def comment(self, content = ""):
        if content == "":
            return False
        postdata=urllib.urlencode({'content':content, 'hostid':self.__id,
                                   '_rtk':self.__rtk, 'channel':'renren'})
        req = urllib2.Request(url = "http://shell.renren.com/" + self.__id + "/status", data = postdata)
        content = urllib2.urlopen(req)
        return content.read()

    def findFriends(self):
        content = urllib2.urlopen("http://friend.renren.com/groupsdata").read()
        place = content.find("\"friends\": ")
        place2 = content.rfind("specialfriends")
        content = content[place+11:place2]
        place = content.rfind(",")
        content = content[:place]
        jsonList = json.loads(content)
        renreninfo = {}
        for i in jsonList:
            renreninfo[str(i["fid"])] = i["fname"]
        return renreninfo
    def visitFriends(self, target={}):
        if type(target) == type({}):
            if target == {}:
                friends = self.findFriends()
            else:
                friends = target
        elif type(target) == type([]):
                friends = target
        else:
            return False
        count = 0
        for i in friends:
            count += 1
            if count == 100:
                count = 0
                self.__showPic()
            urllib2.urlopen(url = "http://www.renren.com/" + i)
            print friends[i],
        return True

    def RP(self, num = 20, showresult = True):
        postdata=urllib.urlencode({'_rtk':self.__rtk})
        req = urllib2.Request(url = "http://renpin.renren.com/action/collectrp", data = postdata)
        urllib2.urlopen(req)
        for i in range(num):
            postdata=urllib.urlencode({'_rtk':self.__rtk})
            req = urllib2.Request(url = "http://renpin.renren.com/mall/lottery/dolottery", data = postdata)
            content = urllib2.urlopen(req).read()
            jsonList = json.loads(content)
            if jsonList.has_key("id"):
                RPid = jsonList["id"]
                postdata=urllib.urlencode({'_rtk':self.__rtk, 'id':RPid})
                req = urllib2.Request(url = "http://renpin.renren.com/mall/lottery/use", data = postdata)
                urllib2.urlopen(req)
                if showresult:
                    print jsonList["name"]

    def readStates(self, friendID, page = 0):
        ans = []
        url = "http://status.renren.com/GetSomeomeDoingList.do?userId="
        url = url + str(friendID) + "&curpage=" + str(page)
        content = urllib2.urlopen(url).read()
        jsonList = json.loads(content)
        for j in jsonList["doingArray"]:
            if j.has_key("rootContent"):
                tmp = j["content"] + ":" + j["rootContent"]
            else:
                tmp = j["content"]
            ans.append(cancelHTML(tmp))
        return ans
    def readStatesID(self, friendID, page = 0):
        ans = []
        url = "http://status.renren.com/GetSomeomeDoingList.do?userId="
        url = url + str(friendID) + "&curpage=" + str(page)
        content = urllib2.urlopen(url).read()
        jsonList = json.loads(content)
        for j in jsonList["likeMap"]:
            statusid = j[7:]
            ans.append(statusid)
        return ans

    def readAStatus(self, statusid, renrenid):
        postdata=urllib.urlencode({'doingid':statusid, 'source':statusid, 'owner':renrenid, '_rtk':self.__rtk, 't':3})
        req = urllib2.Request(url = 'http://status.renren.com/feedcommentretrieve.do', data = postdata)
        content = urllib2.urlopen(req).read()
        jsonList = json.loads(content)
        return jsonList["replyList"]
    def readAStatus2(self, statusid, renrenid, limit = 100):
        url = "http://comment.renren.com/comment/xoa2/?type=status&entryId="
        url = url + statusid + "&entryOwnerId=" + renrenid
        url = url + "&desc=false&limit=" + str(limit) + "&offset=0"
        content = urllib2.urlopen(url, timeout = 20).read()
        jsonList = json.loads(content)
        return jsonList["comments"]
    
    def praiseState(self, stateid, ownerid):
        url = "http://like.renren.com/addlike?gid="
        url = url + "status_" + str(stateid)
        url = url + "&uid=" + self.__id
        url = url + "&owner=" + ownerid + "&type=6"
        content = urllib2.urlopen(url).read()
        return content
    def praiseShare(self, shareid, ownerid):
        url = "http://like.renren.com/addlike?gid="
        url = url + "share_" + str(shareid)
        url = url + "&uid=" + self.__id
        url = url + "&owner=" + ownerid + "&type=3"
        content = urllib2.urlopen(url).read()
    def readNew(self, begin = 0, limit = 30):
        postdata=urllib.urlencode({'begin':begin, '_rtk':self.__rtk, 'limit':limit})
        req = urllib2.Request(url = "http://www.renren.com/feedretrieve3.do", data = postdata)
        content = urllib2.urlopen(req).read()
        return content
    def __showPic(self):
        try:
            import cv2.cv as cv
        except:
            return "Need OpenCV"
        content = urllib2.urlopen("http://www.renren.com/validateuser.do").read()
        place = content.find("http://icode.renren.com/getcode.do?t=ninki&rnd=")
        place2 = content.find("\"/>", place)
        content = content[place: place2]
        filedata = urllib2.urlopen(content).read()
        imagefiledata = cv.CreateMatHeader(1, len(filedata), cv.CV_8UC1)
        cv.SetData(imagefiledata, filedata, len(filedata))
        img0 = cv.DecodeImage(imagefiledata, cv.CV_LOAD_IMAGE_COLOR)
        cv.ShowImage("captchas", img0)
        cv.WaitKey()
        captchas = raw_input("Please enter the captchas:")
        cv.DestroyAllWindows()
        postdata=urllib.urlencode({"id":self.__id, "icode":captchas})
        req = urllib2.Request(url = "http://www.renren.com/validateuser.do", data = postdata)
        content = urllib2.urlopen(req).read()


    def getNotify(self, needDetail = True,begin = 0, limit = 20):
        url = "http://notify.renren.com/rmessage/get?getbybigtype=1&bigtype=1&limit="
        url = url + str(limit) + "&begin=" + str(begin) + "&view=16"
        content = urllib2.urlopen(url).read()
        jsonList = json.loads(content)
        if needDetail:
            return jsonList
        else:
            notify = []
            for i in jsonList:
                notify.append(cancelHTML(i["content"]))
            return notify

    def removeNotify(self, url):
        return urllib2.urlopen(url).read()

    def readAReply(self, data):
        owner = data["owner"]
        source = data["doingId"]
        secondaryReplyId = data["secondaryReplyId"]
        ans = self.readAStatus2(source, owner, 300)
        for i in ans:
            if str(int(i["commentId"])) == secondaryReplyId:
                return i["content"].encode("utf8"), i["authorName"].encode("utf8")
        return False

    def waitComet(self, timeout = 200):
        url = "http://wpi.renren.com/comet_get?mid=0&ins&_rtk=" + self.__rtk
        print cancelHTML(urllib2.urlopen(url).read()), time.ctime()
        url = "http://wpi.renren.com/comet_get?mid=" + str(self.__mid) + "&_rtk=" + self.__rtk
        try:
            content = urllib2.urlopen(url, timeout = timeout).read()
        except:
            return self.waitComet(timeout)
        self.__mid += 1
        if self.__mid > 20:
            self.__mid = 1
        content = json.loads(cancelHTML(content))
        return content
    
    def __typeChange(self, n):
        b = str(n)[:1]
        if b == "2":
            b = n
        a = {"1":"share", "5":"status", "7":"photo", "6":"blog",
             "2038":"photo", "2008":"status", "2006":"share", "2012":"blog",
             "2013":"album", "2036":"share", "2032":"share", "2005":"share"}
        if a.has_key(b):
            return a[b]
        return False
    def reply(self, data):
        if data.has_key("type"):
            goaltype = data["type"]
        else:
            goaltype = self.__typeChange(data["stype"])

        if goaltype ==  False:
            return data
        if not data.has_key("replyTo"):
            postdata=urllib.urlencode({"content":data["content"], "entryOwnerId":data["entryOwnerId"],
                                       "entryId":data["entryId"], "_rtk":self.__rtk, "type":goaltype})
        else:
            postdata=urllib.urlencode({"entryOwnerId":data["entryOwnerId"], "content":data["content"],
                                       "entryId":data["entryId"], "_rtk":self.__rtk, "type":goaltype,
                                       "replyTo":data["replyTo"], "replyName":data["replyName"],
                                       "secondaryReplyId":data["secondaryReplyId"]})
        req = urllib2.Request(url = "http://comment.renren.com/comment/xoa2/create", data = postdata)
        content = urllib2.urlopen(req).read()
        return content
    def feedsubscribe(self, limit = 1):
        url = "http://www.renren.com/feedsubscribe.do"
        postdata = "limit=" + str(limit) + "1&sub=1&_rtk=" + self.__rtk
        content = urllib2.urlopen(url = url, data = postdata).read()
        return content
    def block(self, renrenid):
        url = "http://friend.renren.com/j_f_add_block"
        postdata = "id=" + renrenid + "&_rtk=" + self.__rtk
        content = urllib2.urlopen(url = url, data = postdata).read()
        return "This action has no return."
    def friend_of_friend(self, friendID, pn):
        url = "http://friend.renren.com/friend/api/getotherfriendsdata"
        
        postdata = "p={ \"fid\":\"" + friendID + "\",\"pz\":\"24\",\"type\":\"WEB_FRIEND\",\"pn\":\"" + str(pn) + "\"}" + "&_rtk=" + self.__rtk
        #print postdata
        content = urllib2.urlopen(url = url, data = postdata).read()
        return content
    def Keyword_search(self, keyword, offset):
        url = "http://browse.renren.com/sAjax.do?ajax=1&q=" + keyword
        url += "&p=&s=0&u=" + self.__id + "&act=search&offset=" + str(offset) + "&sort=0"
        return urllib2.urlopen(url).read()

if __name__ == '__main__':
    print 1
    a = renren('', '')
    a.login()
    for i in a.readStates(287048324):
        print i
        
        
