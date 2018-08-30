import urllib2
import renren
import time

def writeText(s, filename):
    f = open(filename, 'a')
    f.write(s + '\n')
    f.close()

def recursion1(a, renrenid, page):
    try:
        statesID = a.readStatesID(renrenid, page)
        states = a.readStates(renrenid, page)
        return statesID, states
    except:
        print 'Network connect error. Retry at 1.'
        time.sleep(2)
        return recursion1(a, renrenid, page)

def recursion2(a, statesID, renrenid):
    try:
        c = a.readAStatus2(statesID, renrenid)
        return c
    except:
        time.sleep(2)
        print 'Network connect error. Retry at 2.'
        return recursion2(a, statesID, renrenid)        

def main():
    renrenid = raw_input('Please input your Renren ID: ')

    #renrenid = '265575649'
    a = renren.renren('290475975@qq.com', 'madokakami')
    print 'Try to login.'
    a.login()
    page = 0
    statesID = ['init']
    while statesID:
        print 'page', page
        statesID, states = recursion1(a, renrenid, page)
        statesID.sort(reverse = True)
        for i in xrange(len(states)):
            try:
                print states[i]
            except:
                pass
            c = recursion2(a, statesID[i], renrenid)
            writeText(states[i].encode('utf8'), renrenid + '.txt')
            for j in c:
                writeText(j['authorName'].encode('utf8') + ' ' + j['content'].encode('utf8'), renrenid + '.txt')
            writeText('='*20, renrenid + '.txt')
        page += 1

main()

