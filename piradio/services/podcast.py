import xml.etree.cElementTree as ET
import urllib2


def load_podcast(url):
    xmldata = urllib2.urlopen(url)
    tree = ET.parse(xmldata)
    episodes = []
    for item in tree.findall('./channel/item'):
        title = item.findall('title')[0].text
        url = item.findall('enclosure')[0].get('url')
        episodes.append((title, url))
    return episodes

# print load_podcast('http://domian.alpha-labs.net/domian.rss')
