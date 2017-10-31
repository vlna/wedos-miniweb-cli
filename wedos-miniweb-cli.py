#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  wedos-miniweb-cli.py
#  
#  Copyright 2017 Vladimír Návrat
#  
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  
  
# parameters: single, path, verbose, domain

import netrc
import urllib, urllib2, cookielib
import re
import getopt, os, sys
import time

domain=''
path = '.'
single = ''
verbose = False
operation = 'upload'
wopener = ''
baseurl = 'https://client.wedos.com'
domainid = ''
extensions = [ 'doc', 'docx', 'docm', 'xls', 'xlsx', 'xlsm', 'odt', 'ods', 'odp', 'pdf', 'txt', 'gif', 'jpg', 'jpeg', 'png', 'css', 'js', 'ico', 'swf', 'ttf', 'eof', 'eot', 'svg', 'woff', 'less', 'xml', 'htc' ]


def listroot(link):
    # returns list of tuples with filename (always *.html), type (always f), last mod time, delete link (if possible)
    listofpages = []
    content = wopener.open(link).read()
    
    plines = re.compile('<tr.*list_row.*miniweb-edit.*<td>')
    mlines = plines.findall(content)

    ppage = re.compile('[^<]*')
    for idx, i in enumerate(mlines):
        d = (i.split('>'))
        if idx==0:
            page = ppage.findall(d[10])[0]
            listofpages.append( (page + '.html', 'f', time.strptime(ppage.findall(d[14])[0], '%d.%m.%Y %H:%M:%S'), '' ) )
        else:
            page = ppage.findall(d[14])[0]
            # TODO: add delete link
            listofpages.append( (page + '.html', 'f', time.strptime(ppage.findall(d[18])[0], '%d.%m.%Y %H:%M:%S'), '' ) )
    return listofpages

def listpageupdatelinks(link):
    # returns list of tuples with filename (always *.html), link
    listoflinks = []
    content = wopener.open(link).read()
    
    plines = re.compile('<tr.*list_row.*miniweb-edit.*<td>')
    mlines = plines.findall(content)

    ppage = re.compile('[^<]*')
    for idx, i in enumerate(mlines):
        d = (i.split('>'))
        if idx==0:
            page = ppage.findall(d[10])[0]
        else:
            page = ppage.findall(d[14])[0]
        
        editor = wopener.open ('https://client.wedos.com/domain/miniweb-edit.html?id=455169&page=' + page + '&editor=t')
        
        content = editor.read()
        
        ppageuploadlink = re.compile('/domain/miniweb-edit\.html.*exh.[0-9a-f]*')
        mpageuploadlink = ppageuploadlink.findall(content)[0]

    return listoflinks

def listfiles(link, path):
    listoffiles = []

    if path == '':
        content = wopener.open(link).read()
    else:
        content = wopener.open(link + '&fm_path=' + path).read()
    
    plines = re.compile('<tr.*list_row.*fileman_item.*<td>')
    mlines = plines.findall(content)
    
    pdeletelink = re.compile('/domain/miniweb\.html.*fm_delete.*exh.*fm_target=')
    mdeletelink = pdeletelink.findall(content)[0]

    pfile = re.compile('[^<]*')
    for idx, i in enumerate(mlines):
        d = (i.split('>'))
        if d[12][:3] == 'DIR':
            dir = pfile.findall(d[9])[0].replace('[', '').replace(']', '')
            
            listoffiles.append( ('files/' + path.replace('%2F', '/') + dir, 'd', '', baseurl + mdeletelink + dir ) )
            sublist = ( listfiles(link, path + dir + '%2F') )
            if len(sublist) > 0:
                listoffiles = listoffiles + sublist
        else:
            file = pfile.findall(d[9])[0]
            listoffiles.append( ('files/' + path.replace('%2F', '/') + file, 'f', time.strptime(pfile.findall(d[14])[0], '%d.%m.%y %H:%M'), baseurl + mdeletelink + file ) )
#            if path == 'test2%2Ftest3%2F' :
#                wopener.open(baseurl + mdeletelink + file)
    return listoffiles

def creators(link, path):
    listofcreators = []

    if path == '':
        content = wopener.open(link).read()
    else:
        content = wopener.open(link + '&fm_path=' + path).read()

    pcreatedir = re.compile('/domain/miniweb\.html[^ ]*fm_mkdir[^ ]*exh.*fm_name=')
    mcreatedir = pcreatedir.findall(content)[0]

    puploadfile = re.compile('/domain/miniweb\.html[^ ]*fm_process&amp[^ ]*exh.[0-9a-f]*')
    muploadfile = puploadfile.findall(content)[0]

    listofcreators.append( ('files/' + path.replace('%2F', '/') , mcreatedir, muploadfile) )
    
    plines = re.compile('<tr.*list_row.*fileman_item.*<td>')
    mlines = plines.findall(content)
    
    pfile = re.compile('[^<]*')
    for idx, i in enumerate(mlines):
        d = (i.split('>'))
        if d[12][:3] == 'DIR':
            dir = pfile.findall(d[9])[0].replace('[', '').replace(']', '')
            
            sublist = ( creators(link, path + dir + '%2F') )
            if len(sublist) > 0:
                listofcreators = listofcreators + sublist    
    
    return listofcreators

def updatepage(pagename, pagecontent):
    # page MUST exist
    editor = wopener.open (baseurl + '/domain/miniweb-edit.html?id=' + domainid + '&page=' + pagename + '&editor=t')
    
    content = editor.read()
    
    ppageuploadlink = re.compile('/domain/miniweb-edit\.html.*page_save.*exh.[0-9a-f]*')
    mpageuploadlink = ppageuploadlink.findall(content)
    
    if len(mpageuploadlink) == 0:
        return 1 # error / unable find upload link

    wpagecontent = urllib.urlencode({'page_content' : pagecontent})
    wopener.open (baseurl + mpageuploadlink[0].replace('&amp;', '&'),  wpagecontent)       
    
    return 0 # probably OK

def createpage(pagename,  pagecontent):
    # creates page (if not exists) and updates it (if pagecontent<>''), 
    newpage = wopener.open(baseurl + '/domain/miniweb.html?id=' + domainid + '&page=_new')
    content = newpage.read()
    
    pcreatenewpage = re.compile('/domain/miniweb\.html.*page.create.*exh.[0-9a-f]*')
    mcreatenewpage = pcreatenewpage.findall(content)[0]
    
    wnewpagename = urllib.urlencode({'name' : pagename})
    creation = wopener.open (baseurl + mcreatenewpage.replace('&amp;', '&'),  wnewpagename)
    
    if pagecontent != '':
        updatepage(pagename, pagecontent)



def main():

    usage = """Usage:
    %s -c -p path                           : check local files
    %s -d domain -l                         : list remote files
    %s -d domain -p path                    : complete upload
    %s -d domain -p path -s /single.html    : single file upload
    %s -d domain -s files/single/           : remote folder creation
    
    -h, --help : help
    -c, --check : check local structure and filenames
    -d, --domain= : domain name
    -l, --list : list remote pages and files and dirs
    -p, --path= : path to local dir for upload/download
    -s, --single= : remote single file upload/download/delete, folder create/delete 
    -v, --verbose : verbose output
        --delete : delete remote page(s)/file(s)
        --username : username
        --password : password""" % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:hlp:s:v', ['domain=', 'help', 'list', 'path=', 'single=', 'verbose', 'delete', 'username=', 'password='])
    except getopt.error, msg:
        print >>sys.stderr, msg
        print >>sys.stderr, usage
        sys.exit(1)


    wusername = ''
    wpassword = ''

    for o, a in opts:
        print o
        print a
        if o == "--help" or o == "-h":
            print >>sys.stdout, usage
            sys.exit(0)

        if o == "--domain" or o == "-d":
            global domain
            domain = a

        if o == "--path" or o == "-p":
            global path
            path = a

        if o == "--single" or o == "-s":
            global single
            single = a

        if o == "--verbose" or o == "-v":
            global verbose
            verbose = True

        global operation
        if o == "--delete":
            operation = 'delete'

        if o == "--list" or o == "-l":
            operation = 'list'

        if o == "--username":
            wusername = a
        
        if o == "--password":
            wpassword = a

    if domain == '':
        print('No domain found. Use command line parameters -d or --domain.')
        sys.exit(1)

    if wusername == '' or wpassword == '':
        credentials = netrc.netrc()
        auth = credentials.authenticators("client.wedos.com")
        if auth:
            if wusername == '': wusername = auth[0]
            if wpassword == '': wpassword = auth[2]
        else:
            print('No credentials found. Update your .netrc file or use command line parameters.')
            sys.exit(1)


    if verbose:
        print('Logging in as ' + wusername)

    global wopener
    wcookies = cookielib.CookieJar()
    wopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(wcookies))
  
    #get cookies and login form
    wfirst = wopener.open('https://client.wedos.com/home/')
    
    wlogindata = urllib.urlencode({'login' : wusername, 'passwd' : wpassword})

    wpage = wfirst.read()
    
    p = re.compile('https.*exec.*execute[^"]*')
    match = p.findall(wpage)
   
    #log in and get cookie
    wlogin = wopener.open(match[1].replace('&amp;', '&'), wlogindata)
    # check propper login
    logout = re.findall('logout\.html.exec.execute.*exh.[0-9a-f]*',wlogin.read())
    if len(logout) == 0:
        print('It looks like you are not logged in, check your credentials.')
        sys.exit(1)
        

    #list available domains
    wdomains = wopener.open(baseurl + '/domain/')

    p = re.compile('<tr.*detail\.html.*status_active.*<td>')
    match = p.findall(wdomains.read())

    if len(match) == 0:
        print('No domains found')
        sys.exit(1)

    p1 = re.compile('detail\.html[^"]*')
    p2 = re.compile('[0-9][0-9]*') #number
    p3 = re.compile('[^<]*')


    for i in match:
        d = (i.split('>'))
        # d[5] = link, d[10] = number, d[13] = name
        if verbose:
            print('Domain found: ' + p3.findall(d[13])[0])
        if p3.findall(d[13])[0] == domain:
            global domainid
            domainid = p2.findall(d[5])[0]
    
    if domainid == '':
        print('Selected domain is not available.')
        sys.exit(1)
    
    #dirs and files creator in files
    dfcreators = creators(baseurl + '/domain/miniweb.html?id=' + domainid + '&files=1', '')

    listofall = listroot(baseurl + '/domain/miniweb.html?id=' + domainid + '&pages=1') + listfiles(baseurl + '/domain/miniweb.html?id=' + domainid + '&files=1', '')
    
    if operation == 'list':
        for f, t, m, d in listofall:
            if t == 'd':
                print(f + '/')
            else:
                print(f)
        return 0
   
    if operation == 'delete' and single != '':
        #if single[-5] = '.html'
        for f, t, d in listofall:
            if f == single or f == single + '/':
                wopener.open(d)
                print f + ' deleted'
        return 0

    if operation == 'upload' and single == '' and path != '':
        for root, dirs, files in os.walk(path):
            dircreated = False
            for name in dirs:
                print(os.path.join(root, name))
                print 'create remote folder if missing'
                remotepath = os.path.join(root, name)[len(path):]
                if remotepath[0] == '/':
                    remotepath = remotepath[1:]
                if remotepath [0:6] == 'files/':
                    dirs = ''
                    #[list(t) for t in zip(*l)]
                    dirs = list (zip(*dfcreators)[0])
                    if remotepath + '/' not in dirs:
                        updir = remotepath.rsplit('/', 1)[0] + '/'
                        if dirs.index(updir)>=0:
                            dcreator = dfcreators[dirs.index(updir)][1].replace('&amp;', '&').replace('%2F', '/')
                            print 'create remote folder'
                            print (baseurl + dcreator + remotepath.rsplit('/', 1)[1])
                            wopener.open(baseurl + dcreator + remotepath.rsplit('/', 1)[1])
                            dircreated = True
                else:
                    print('Unable to create folder ' + remotepath)
                
            print 'refresh dfcreators'
            if dircreated:
                dfcreators = creators(baseurl + '/domain/miniweb.html?id=' + domainid + '&files=1', '')
             
            for name in files:
                print(os.path.join(root, name))
                remotepath = os.path.join(root, name)[len(path):]
                if remotepath[0] == '/':
                    remotepath = remotepath[1:]
                if remotepath [0:5] == 'files/':
                    print 'file upload'
                if remotepath[-5:] == '.html' and remotepath.find('/') == -1:
                    with open(os.path.join(root, name), 'r') as f:
                        filecontent = f.read()
                    f.closed
                    createpage (remotepath[:-5], filecontent)
        return 0

    
    if single != '':
        if operation == 'upload' and single[-1] == '/':
            print 'create folder'


    p = re.compile('<tr.*list_row.*miniweb-edit.*<td>')
    match = p.findall(wroot.read())
    
    for idx, i in enumerate(match):
        d = (i.split('>'))
        if idx==0:
            page = p3.findall(d[10])[0]
        else:
            page = p3.findall(d[14])[0]
            
        if page == 'tmp':
            print page

    if operation == 'delete' and single != '':
        for idx, i in enumerate(match):
            d = (i.split('>'))
            pdelete = re.compile('/domain/miniweb\.html[^\\\\\']*')
            if idx==0:
                page = p3.findall(d[10])[0]
            else:
                page = p3.findall(d[14])[0]
                link = pdelete.findall(d[11])[0]
                
                if page == single or page + '.html' == single:
                    #delete page here
                    wdelete = wopener.open(baseurl + link.replace('&amp;', '&'))
                    print page + ' deleted'


    print link


    
    return 0


if __name__ == '__main__':
	main()
