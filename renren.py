import urllib.request, json, re, multiprocessing, os

def HTML_tag(s):
    a = re.sub('<.+?>', '', s)
    return a

def reply(cookie, userId, entryId, commentsType):
    l = []
    c = openurl('http://comment.renren.com/comment/xoa2?limit=100&desc=true&offset=0&replaceUBBLarge=true&type={2}&entryId={0}&entryOwnerId={1}'.format(entryId, userId, commentsType), cookie)
    if 'comments' not in c: return reply(cookie, userId, entryId, commentsType)
    comments = c['comments']
    for i in comments:
        l.append((i['time'], i['authorName'], HTML_tag(i['content'])) )
    return l

def openurl(url, cookie, isjson=True):    
    headers = {'Cookie': cookie, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
    request = urllib.request.Request(url, headers=headers)
    try: c = urllib.request.urlopen(request, timeout=10)
    except: return openurl(url, cookie, isjson)
    if isjson: c = json.loads(c.read().decode('utf8'))
    else: c = c.read().decode('utf8')
    return c

def savepic(url, cookie, savePath):    
    headers = {'Cookie': cookie, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
    request = urllib.request.Request(url, headers=headers)
    try: c = urllib.request.urlopen(request, timeout=10)
    except: return savepic(url, cookie, savePath)        
    f = open(savePath, 'wb')
    f.write(c.read())
    f.close()


def func(cookie, userId, cnt):
    print('【状态】第{0}页开始'.format(cnt))
    s = ''
    c = openurl('http://status.renren.com/GetSomeomeDoingList.do?userId={0}&curpage={1}'.format(userId, cnt), cookie)
    status = c['doingArray']
    for i in status:
        if 'content' not in i: print(c)
        s += i['dtime'] + '\n'
        s += HTML_tag(i['content']) + '\n'
        if 'rootContent' in i: s += HTML_tag(i['rootContent']) + '\n'
        s += '+'*10+'\n'
        l = reply(cookie, userId, int(i['id']), 'status')
        s += '\n'.join([i[0]+'|'+i[1]+'：'+i[2] for i in l]) + '\n'
        s += '='*10 + '\n'
    print('【状态】第{0}页完成'.format(cnt))
    return s

def statusList(cookie, userId):
    c = openurl('http://status.renren.com/GetSomeomeDoingList.do?userId={0}&curpage=0'.format(userId), cookie)
    page_cnt = c['count']
    page_cnt = page_cnt//20 + 1
    print('状态总共页数：', page_cnt)
    results = []
    pool = multiprocessing.Pool(80)
    for cnt in range(page_cnt): results.append(pool.apply_async(func, (cookie, userId, cnt)))
    pool.close()
    pool.join()
    f = open('状态.txt', 'w', encoding = 'utf8')
    f.write(''.join([i.get() for i in results]))
    f.close()

def blogSave(cookie, userId, cnt):
    print('【日志】第{0}页开始'.format(cnt))
    content = openurl('http://blog.renren.com/blog/{0}/blogs?curpage={1}'.format(userId, cnt), cookie)
    for i in content['data']:
        blogId = int(i['id'])
        c = openurl('http://blog.renren.com/blog/{0}/{1}'.format(userId, blogId), cookie, False)
        c = c.replace('\n', '')
        artical = re.findall('<!--日志内容-->.+?<!--上一篇、下一篇-->', c)[0]
        s = '<hr />'
        l = reply(cookie, userId, blogId, 'blog')   
        s += '\n'.join(['<p>'+i[0]+'|'+i[1]+'：'+i[2]+'</p>' for i in l])
        f = open('blog/'+str(blogId)+'.html', 'w', encoding='utf8')
        f.write(artical+s)
        f.close()
    print('【日志】第{0}页完成'.format(cnt))

def blogList(cookie, userId):
    if not os.path.exists('blog'): os.makedirs('blog')
    c = openurl('http://blog.renren.com/blog/{0}/blogs?curpage=0'.format(userId), cookie)
    page_cnt = c['count']
    page_cnt = page_cnt//10 + 1
    print('Blog总共页数：', page_cnt)
    pool = multiprocessing.Pool(15)
    for cnt in range(page_cnt): pool.apply_async(blogSave, (cookie, userId, cnt))
    pool.close()
    pool.join()

def getPhoto(cookie, userId, albumId):
    c = openurl('http://photo.renren.com/photo/{0}/album-{1}/v7'.format(userId, albumId), cookie, False)
    title = re.findall('<title>.+?</title>', c)[0]
    title = title.replace('</title>', '').replace('<title>人人网 - 浏览相册 - ', '')
    print('【相册】开始', title)
    if not os.path.exists('photo/' + title): os.makedirs('photo/' + title)
    page_cnt = int(re.findall('\'photoCount\':.+?,', c)[0].split(':')[-1][:-1])
    page_cnt = page_cnt//20+1
    s = '<html><body><table border=1>'
    for cnt in range(page_cnt):
        c = openurl('http://photo.renren.com/photo/{0}/album-{1}/bypage/ajax/v7?page={2}&pageSize=20'.format(userId, albumId, cnt), cookie)
        print('【相册】', title, '第{0}页，共{1}页'.format(cnt, page_cnt))
        for i in c['photoList']: 
            #print(title, i['photoId'], i['url'])
            savePath = title+'/'+i['url'].split('/')[-1]
            savepic(i['url'], cookie, 'photo/'+savePath)
            l = reply(cookie, userId, i['photoId'], 'photo')
            s += '<tr><td width=60%><img src=\'{0}\'>'.format(savePath) + '</td><td width=40%>'
            s += '\n'.join(['<p>'+i[0]+'|'+i[1]+'：'+i[2]+'</p>' for i in l]) + '</td></tr>'
    s += '</table></body></html>'
    f = open('photo/'+title+'.html', 'w', encoding='utf8')
    f.write(s)
    f.close()
    print('【相册】结束', title)
    return(title)

def photoList(cookie, userId):
    c = openurl('http://photo.renren.com/photo/{0}/albumlist/v7?offset=0&limit=100'.format(userId), cookie, False)
    albumIds = re.findall('\"albumId\":\".+?\"', c)
    albumIds = [i.split('\"')[-2] for i in albumIds]
    print('相册总数：', len(albumIds))
    #此处偷懒了，不平衡的多进程。
    pool = multiprocessing.Pool(15)
    for cnt in albumIds: pool.apply_async(getPhoto, (cookie, userId, cnt))
    pool.close()
    pool.join()
    
if __name__ == '__main__':
    multiprocessing.freeze_support()
    print('欢迎使用！由于人人被卖了，接下来不知道什么时候会倒闭，这个程序可以帮助用户把自己的人人网的状态、相册、文章给保存下来。')
    print('请先阅读使用指南于：https://github.com/ShiShuyang/RenRenCrawler')
    print('EXE文件下载地址：https://github.com/ShiShuyang/RenRenCrawler/releases')
    print('如果长时间卡在用户ID上，说明cookie.txt存在问题，请重新复制。')
    if os.path.exists('cookie.txt'):
        f = open('cookie.txt', 'r')
        cookie = f.read().strip()
        f.close()
        userId = re.findall('; id=.+?;', cookie)[0][5:-1]
        print('用户ID：', userId)
        statusList(cookie, userId)
        blogList(cookie, userId)
        photoList(cookie, userId)
        print('已完成')
    else:
        print('【错误】没有找到cookie.txt，已经帮你新建好了空文件，请按照阅读使用指南填入相关内容。')
        f = open('cookie.txt', 'w')
        f.close()
    os.system("pause")
