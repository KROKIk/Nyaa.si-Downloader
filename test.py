import feedparser

rrs = 'http://nyaa.si/?page=rss&q=[HorribleSubs]+[1080p]'
rrs = 'https://horriblesubs.info/rss.php?res=1080'
feed = feedparser.parse(rrs)

for post in feed['entries']:
    print(post['title'])