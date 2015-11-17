#Erik McLaughlin
#11/15/2015

from lxml import html
from lxml.html.clean import clean_html
import requests
import datetime
import requests
import sys
import mysql.connector

def main():
    
    #Make sure the files are encoded in UTF-8
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    now = datetime.datetime.now()
    
    tableName = "reports"   #MySQL table to insert into
    
    #MySQL settings
    mysqlconfig = {
                    'user': '',
                    'password': '',
                    'host': '127.0.0.1',
                    'database': 'police',
                    'raise_on_warnings': False,
    }
    cnx = mysql.connector.connect(**mysqlconfig)
    cursor = cnx.cursor()
    
    #Retrieve lists of URLs and output file names
    urls = getURLs()
    fnames = getFNames()
    
    #Array to hold generated INSERT statements
    sql_cmds = []
    
    for i in range(len(urls)):
        tree = getData(urls[i])                                             #Retrieve entire HTML text from page
        sql_cmds.append(parseFile(tree, fnames[i], cursor, tableName))      #Send HTML to parseFile() method and add output to array
    
    print "\n\nInserting values into table '" + tableName + "'..."
    for i in sql_cmds:
        for j in i:
            #print repr(j)
            cursor.execute(j)   #Execute MySQL statements
    cnx.commit()    #Commit changes to database
    cursor.close()  
    cnx.close()
    print "\nDone."
    print "Processed %d pages from 7/2009 to %s/%d" % (len(urls), now.month, now.year)
    
    
#   Generates and returns a list of pages to scrape
#   Ranges from June 2009 to the current month and year
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
    
    #Begin with array of pages from 2009
    urls = [
                "http://www.montana.edu/police/policelog/2009/June2009.html",
                "http://www.montana.edu/police/policelog/2009/July2009.html",
                "http://www.montana.edu/police/policelog/2009/August2009.html",
                "http://www.montana.edu/police/policelog/2009/September2009.html",
                "http://www.montana.edu/police/policelog/2009/October2009.html",
                "http://www.montana.edu/police/policelog/2009/November2009.html",
                "http://www.montana.edu/police/policelog/2009/December2009.html"
                ]
    #Add pages to array from 2010 to the last complete year (2014 as of writing)
    for yr in range(2010, curYear):
        for mo in months:
            url = "http://www.montana.edu/police/policelog/%d/%s%d.html" % (yr, mo, yr)
            urls.append(url)
    #Add pages to array from current year
    for m in range(0, now.month):
        yr = curYear
        mo = months[m]
        url = "http://www.montana.edu/police/policelog/%s/%s%s.html" % (yr, mo, yr)
        urls.append(url)
        
    return urls

    
#   Same as getURLs() but without the URL formatting. 
#   These two methods could probably be condensed into one at some point
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

#   Retrieve page content from passed url string, remove extra tags and return a lxml.html tree object
def getData(url):
    print "Processing %s" % url
    page = requests.get(url)
    
    #Create tree object from page content with excess tags removed
    tree = html.fromstring(
            page.content.replace('<span>', '')
                .replace('<p>', '')
                .replace('<br>', '')
                .replace("'", ''))
    return tree
    
#   Main functionality method
#   
def parseFile(tree, writeFileName, cursor, tableName):
    #Array containing names of table columns
    colNames = [    'Case Number        ',
                    'Report Date/Time   ',
                    'Occurred Date/Time ',
                    'Incident           ', 
                    'Location           ',
                    'Disposition        '
    #Extra empty elements in case table row is malformed or parsed incorrectly
    ,'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']; 
    
    #Folder names for output files
    outputFolder = 'output_SQL/'
    skippedFolder = 'skipped/'
    
    #Create output files
    outFile = open(outputFolder + writeFileName, "wb")
    outFileSkipped = open(outputFolder + skippedFolder + writeFileName, "wb")
    
    
    recordedRows = 0
    skippedRows = 0
    
    #Array to hold generated SQL statements
    sqlStatements = []
    
    #HTML parsing code... This might get rough
    tbl = tree.xpath('//section[@id=\'maincontent\']')  #tbl[] will only have one element, the table with the attribute 'maincontent'
    tr = tbl[0].xpath('//tbody/tr')                     #Select all <tr> elements within the <tbody> tag       
    for i in range(1,len(tr)):          
        td = tr[i].xpath('td//text()')                      #Select the text of each <td> element
        if len(td) == 6 and td[0] != '':                    #Make sure there are exactly 6 elements in the row and the first isn't empty
            statement = "INSERT INTO "+ tableName +" VALUES("  #SQL statement
            for j in range(len(td)-1):                      
                g = td[j].strip()           #strip leading and trailing whitespace
                h = " ".join(g.split())     #strip extra whitespace from the middle of string
                statement = statement + "'" + h + "', " #Add formatted values to statement string
            
            #We have to process the last element separately because we need it to end without a comma and with closing parentheses
            g = td[len(td)-1].strip()
            h = " ".join(g.split())
            statement = statement + "'" + h + "')"
            
            #Write statement to file
            outFile.write(statement)
            outFile.write(";\n\n")
            
            recordedRows = recordedRows + 1
            sqlStatements.append(statement) #add statement to return array
        
        #Document malformed row values. We don't add these to the SQL statement array, but we write them to a file so we can see what's wrong
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
    #Close file objects
    outFile.close()
    outFileSkipped.close()
    
    print "%d/%d rows skipped" % (skippedRows, recordedRows + skippedRows)  #print the numbers of successful and malformed rows
    
    return sqlStatements    #Return the array of statements

main()