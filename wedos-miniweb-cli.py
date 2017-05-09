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
  

# parameters to do: single, path, verbose, domain

import netrc
import urllib, urllib2, cookielib
import re

def main():

    credentials = netrc.netrc()
    auth = credentials.authenticators("client.wedos.com")
    if auth:
        wusername = auth[0]
        wpassword = auth[2]

    print(wusername)
    print(len(wpassword))

    wcookies = cookielib.CookieJar()
    wopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(wcookies))
    
    wfirst = wopener.open('https://client.wedos.com/home/')
    
    wlogindata = urllib.urlencode({'login' : wusername, 'passwd' : wpassword})

    print(wcookies)
    wpage = wfirst.read()
    
    p = re.compile('https.*exec.*execute[^"]*')
    match = p.findall(wpage)
   
    print(match)
   
    wlogin = wopener.open(match[1].replace('&amp;', '&'), wlogindata)

    wdomains = wopener.open('https://client.wedos.com/domain/')

    p = re.compile('<tr.*detail\.html.*status_active.*<td>')
    match = p.findall(wdomains.read())

    if len(match) == 0:
        print 'No domains found'

    p1 = re.compile('detail\.html[^"]*')
    #p2 = re.compile('[^<]*') #order number
    p3 = re.compile('[^<]*')


    for i in match:
        d = (i.split('>'))
        # d[5] = link, d[10] = order number, d[13] = name
        #tmp = p3.findall(d[13])
        if p3.findall(d[13])[0] == 'domain.eu':
            #tmp = 'https://client.wedos.com/domain/'+p1.findall(d[5])[0]
            wroot = wopener.open('https://client.wedos.com/domain/'+p1.findall(d[5])[0].replace('detail', 'miniweb', 1)+'&pages=1')
        
     
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

    
    return 0


if __name__ == '__main__':
	main()

