import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url=input("Enter URL: ")
count=int(input("Enter count:"))
position=int(input("Enter position:"))
html = urllib.request.urlopen(url, context=ctx).read()


taglist=list()

for i in range(count):
    print ("Retrieving:",url)
    import urllib.request
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    alltags=soup('a')
    for tag in alltags:
        taglist.append(tag)
    url = taglist[position-1].get('href', None)
    del taglist[:]
print ("Retrieving:",url)
