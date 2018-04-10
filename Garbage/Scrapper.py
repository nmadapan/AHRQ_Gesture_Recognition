###################################

url='https://www.google.com/'    ##Enter the url to scrap from
depth=2                          ## Enter the depth

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

from bs4 import BeautifulSoup
import urllib
import re


def get_links(url):
    links = []

    html_page = urllib.request.urlopen(url)
    soup = BeautifulSoup(html_page)

    for link in soup.findAll('a', attrs={'href': re.compile("^https://")}):
        links.append(link.get('href'))

    return links


all_links = []
all_links.append(url)
len_beg = len(all_links)

# print(len_beg)
if depth >= 1:
    l2 = get_links(url)
    for k in l2:
        all_links.append(k)

all_links = set(all_links)
all_links = list(all_links)
len_pre = len(all_links)
# print(all_links)
# print(len_pre)

for i in range(depth - 1):
    print(i)
    len_pre = len(all_links)
    for link in all_links[len_beg:len_pre]:
        try:
            l3 = get_links(link)
            for m in l3:
                all_links.append(m)
        except:
            print('')

    len_beg = len_pre

    all_links = set(all_links)
    all_links = list(all_links)
    len_pre = len(all_links)

print(len(all_links), all_links)

b = 0
for link in all_links:
    try:
        page = urlopen(link)
        with open("file_" + str(b) + ".html", 'wb') as f:
            f.write(page.read())
        b += 1
    except:
        print("Website is not allowing to scrape")
