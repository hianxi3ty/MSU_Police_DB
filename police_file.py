#Erik McLaughlin
#11/15/2015

from lxml import html
from lxml.html.clean import clean_html
import requests
import datetime
import requests
import sys


def main():
    reload(sys)
    sys.setdefaultencoding('utf8')
    now = datetime.datetime.now()
    
    urls = getURLs()
    fnames = getFNames()
    successfulRows = 0
    skippedRows = 0
    
    for i in range(len(urls)):
        tree = getData(urls[i])
        rowNums = parseFile(tree, fnames[i])
        successfulRows = successfulRows + rowNums[0]
        skippedRows = skippedRows + rowNums[1]
        
    print "\nDone."
    print "Processed %d pages from 7/2009 to %s/%d" % (len(urls), now.month, now.year)
    print "%d total malformed rows skipped out of %d" % (skippedRows, successfulRows)
def getURLs():
    now = datetime.datetime.now()
    curYear = now.year

    months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
    ]
    curMonth = months[now.month - 1]
    start_urls = [
                "http://www.montana.edu/police/policelog/2009/June2009.html",
                "http://www.montana.edu/police/policelog/2009/July2009.html",
                "http://www.montana.edu/police/policelog/2009/August2009.html",
                "http://www.montana.edu/police/policelog/2009/September2009.html",
                "http://www.montana.edu/police/policelog/2009/October2009.html",
                "http://www.montana.edu/police/policelog/2009/November2009.html",
                "http://www.montana.edu/police/policelog/2009/December2009.html"
                ]
    for yr in range(2010, curYear):
        for mo in months:
            url = "http://www.montana.edu/police/policelog/%d/%s%d.html" % (yr, mo, yr)
            start_urls.append(url)
    for m in range(0, now.month):
        yr = curYear
        mo = months[m]
        url = url = "http://www.montana.edu/police/policelog/%s/%s%s.html" % (yr, mo, yr)
        start_urls.append(url)
        
    return start_urls

def getFNames():
    now = datetime.datetime.now()
    curYear = now.year

    months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
    ]
    curMonth = months[now.month - 1]
    start_fnames = [
                "2009June.txt",
                "2009July.txt",
                "2009August.txt",
                "2009September.txt",
                "2009October.txt",
                "2009November.txt",
                "2009December.txt"
                ]

    for yr in range(2010, curYear):
        for mo in months:
            start_fnames.append("%d%s.txt" % (yr, mo))
    for m in range(0, now.month):
        yr = curYear
        mo = months[m]
        start_fnames.append("%d%s.txt" % (yr, mo))
        
    return start_fnames
def getFile(fileName):
    with open (fileName, "r") as myfile:
        data=myfile.read().replace('\n', '').strip()

def getData(url):
    print "Processing %s" % url
    page = requests.get(url)
    tree = html.fromstring(page.content.replace('<span>', '').replace('<p>', '').replace('<br>', ''))
    return tree
    
def parseFile(tree, writeFileName):
    colNames = [    'Case Number        ',
                    'Report Date/Time   ',
                    'Occurred Date/Time ',
                    'Incident           ', 
                    'Location           ',
                    'Disposition        '
    ,'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']; 
    
    outputFolder = 'output/'
    skippedFolder = 'skipped/'
    
    outFile = open(outputFolder + writeFileName, "wb")
    outFileSkipped = open(outputFolder + skippedFolder + writeFileName, "wb")
    recordedRows = 0
    skippedRows = 0
    
    tbl = tree.xpath('//section[@id=\'maincontent\']')
    tr = tbl[0].xpath('//tbody/tr')
    for i in range(1,len(tr)):
        td = tr[i].xpath('td//text()')
        if len(td) == 6:
            for j in range(len(td)):
                g = td[j].strip()
                h = " ".join(g.split())
                outStr = "%s: %s" % (colNames[j], h)
                #print outStr
                outFile.write(outStr)
                outFile.write("\n")
            outFile.write("\n")
            recordedRows = recordedRows + 1
        else:
            outFileSkipped.write(html.tostring(tr[i]))
            for j in range(len(td)):
                g = td[j].strip()
                h = " ".join(g.split())
                outStr = "%s: %s" % (colNames[j], h)
                #print outStr
                outFileSkipped.write(outStr)
                outFileSkipped.write("\n")
            outFileSkipped.write("\n")
            skippedRows = skippedRows + 1
            #print "Malformed row: %d in %s" % (i, writeFileName)
    outFile.close()
    print "%d/%d rows skipped" % (skippedRows, recordedRows + skippedRows)
    return [recordedRows, skippedRows]

main()