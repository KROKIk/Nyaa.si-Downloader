import requests
import json
import feedparser
import textdistance as td
import transmissionrpc
from datetime import datetime
import config


today = datetime.today().strftime("%d/%m/%Y %H:%M")
url = 'https://graphql.anilist.co'

#TODO pozbyć się tego
media_id = []
id_list = []
title_list = []
magnet_list = []
log_list = []
acc_list = []
match_list = []


query = '''
query ($id: String, $page: Int) { # Define which variables will be used in the query (id)
  Page (perPage: 50, page: $page) { 
    mediaList (userName: $id, status: PLANNING, type: ANIME) {
      mediaId
    }
  }
}
'''

for n in range(10):
    variables = {
        'id': config.anilist_username,
        'page': n,
    }
    # Make the HTTP Api request
    response = requests.post(url, json={'query': query, 'variables': variables})
    json_obj = json.loads(response.text)["data"]["Page"]["mediaList"]
    if not json_obj:
        break
    for mediaid in json_obj:
        media_id.append(mediaid)

query = '''
query ($id: String, $page: Int) { # Define which variables will be used in the query (id)
  Page (perPage: 50, page: $page) { 
    mediaList (userName: $id, status: CURRENT, type: ANIME) {
      mediaId
    }
  }
}
'''
for n in range(10):
    variables = {
        'id': config.anilist_username,
        'page': n,
    }
    # Make the HTTP Api request
    response = requests.post(url, json={'query': query, 'variables': variables})
    json_obj = json.loads(response.text)["data"]["Page"]["mediaList"]
    if not json_obj:
        break
    for mediaid in json_obj:
        media_id.append(mediaid)

for dict in media_id:
    id_list.append(dict['mediaId'])
media_id = id_list
media_id = list(dict.fromkeys(media_id))

#print(len(media_id), media_id)

for anime in media_id:
    query = '''
               query ($id: Int) {
                 Media (id: $id) { 
                   title {
                     romaji
                   }
                 }
               }
               '''

    variables = {
        'id': anime
    }

    response = requests.post(url, json={'query': query, 'variables': variables})
    json_obj = json.loads(response.text)["data"]["Media"]["title"]["romaji"]
    title_list.append(json_obj)
#print(title_list)

try:
    f = open("id.txt", "r")
except FileNotFoundError:
    f = open("id.txt", "w+")
last_id = f.readline()
f.close()

#rrs = 'https://horriblesubs.info/rss.php?res=1080'
rrs = 'http://nyaa.si/?page=rss&q=[HorribleSubs]+[1080p]'
feed = feedparser.parse(rrs)

for post in feed['entries']:
    if post['id'] == last_id:
        break
    best_acc = 0
    best_match = ''
    for anime in title_list:
        acc = td.jaro.similarity(post['title'][15:-17].lower(),  anime.lower())
       # acc = td.sorensen.normalized_similarity(post['title'][15:-17], anime)
       # acc = td.jaccard.normalized_similarity(post['title'][15:-17], anime)
        if acc > best_acc:
            best_acc = acc
            best_match = anime
    if best_acc > 0.75:
        print(best_acc, best_match, "==============", post['title'][15:-17])
        magnet_list.append(post['link'])
        log_list.append(post['title'])
        acc_list.append(best_acc)
        match_list.append(best_match)


f = open("id.txt", "w+")
f.write(feed['entries'][0]['id'])
f.close()
try:
    tc = transmissionrpc.Client(config.transmission_ip, port=config.transmission_ip)
    for link in magnet_list:
        temp_log = log_list[magnet_list.index(link)][15:-17]
        tc.add_torrent(link, download_dir='/usr/local/etc/transmission/home/Downloads/' + temp_log)
except:
    print("Time out Error")
if len(magnet_list) > 0:
    print("Successfully added ", len(magnet_list), " Torrents")
else:
    print("No Torrents added")
f = open("downloaded_anime.log", "a+")
n = 0
for log in log_list:
    f.write("[" + str(today) + "] " + log + " Best match is: " + match_list[n] + " with " + str(acc_list[n] * 100)[:5] + "% Accuracy" + "\n")
    n += 1
f.close()
