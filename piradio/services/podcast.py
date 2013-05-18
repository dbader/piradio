import logging
import xml.etree.cElementTree as elementtree
import urllib2
from piradio.services import base

logger = logging.getLogger('PodcastService')

class PodcastService(base.AsyncService):
    def __init__(self):
        super(PodcastService, self).__init__(tick_interval=24*60*60)

    @staticmethod
    def load_podcast(url):
        logger.info('Loading feed %s', url)
        xmldata = urllib2.urlopen(url)
        tree = elementtree.parse(xmldata)
        episodes = []
        for item in tree.findall('./channel/item'):
            title = item.findall('title')[0].text
            url = item.findall('enclosure')[0].get('url')
            episodes.append((title, url))
        logger.info('Loaded %i episodes from %s', len(episodes), url)
        return episodes

    def tick(self):
        super(PodcastService, self).tick()
        feed_urls = self.subscriptions.keys()
        logger.info('Pulling podcasts from %i feeds', len(feed_urls))
        for feed in feed_urls:
            episodes = self.load_podcast(feed)
            self.notify_subscribers(feed, episodes)
