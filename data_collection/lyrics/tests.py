import re
import bs4
import sys
sys.path.append('../../')
import time
import pickle
import requests
import lyricsgenius
from itertools import cycle
import random
from fake_useragent import UserAgent
from difflib import SequenceMatcher
from utils.SongStream import SongStream


def load_obj(datatype):
    with open(f"{datatype}" + '.pkl', 'rb') as f:
        return pickle.load(f)

# 5.252.161.48	8080
# 35.172.135.29	80
# 178.32.223.164	8118
# 191.101.39.176	80
# 191.101.39.33	80
# 191.101.39.248	80
# 191.101.39.235	80
# 191.101.39.160	80
# 136.226.33.115	80
# 45.178.225.78	80]

def get_url(song, artist):
    temp = '\''
    ua = UserAgent()
    headers = {
        "user-agent": ua.random,
        # 'referer': 'https://www.google.com/'
    }

    query = f'http://google.com/search?q={artist.replace(" ", "+")}+{song.replace(" ", "+").replace(temp, "")}+song+site:genius.com'
    html = requests.get(query).content
    time.sleep(5)
    try:
        url = re.sub(r'-lyrics.*', '-lyrics', bs4.BeautifulSoup(html, 'html.parser').find_all('a')[16]['href'][7:])
        return url
    except:
        return None


def get_lyrics(repair=False):
    def manual_retrieval():
        url = get_url(song, artist)
        if url:
            print(url)
            url_compar = url[19:len(url) - 7]
            control_compar = artist.replace(' ', '-')+'-'+song.replace(' ', '-')

            song_bool = SequenceMatcher(None, control_compar[-len(song):], url_compar[-len(song):]).ratio()
            artist_bool = SequenceMatcher(None, control_compar[:len(artist)], url_compar[:len(artist)]).ratio()
            print(song_bool+artist_bool)
            if song_bool+artist_bool < 1.1:
                print('too diff')
                return None
            try:
                return g.lyrics(song_url=url)
            except:
                print('query issue')
                return None
        else:
            print('query or connection issue')
            return None

    lyrs = load_obj('lyrics')
    rep_count = 0
    count = 0
    g = lyricsgenius.Genius("Y2p-Qam6OpCix8jgS1KHq5SUe85dxdZ_LCBVdz5pOsb2gcCL1btUNsgr6iWAO5Wl")
    g.response_format = 'plain'
    stream = SongStream()
    for ind, s in enumerate(stream):
        print(ind)
        artist = stream[s]['Qual'][0]['artists'][0]['name']
        if lyrs.get(s, None) or not artist or ind < 300:
            continue

        song = re.sub(r'\sfeat.*', '', re.sub(r'\s\(feat.*\)', '', s)).lower()
        artist = artist[0]+artist[1:].lower()
        for char in '.\'’,!?()[]$&\\/\"':
            song = song.replace(char, '')
            artist = artist.replace(char, '')
        query = f'{artist.replace(" ", "-")}-{song.replace(" ", "-")}'

        if repair:
            print(f'https://genius.com/{query}-lyrics')
            lyrs[s] = manual_retrieval()
            if rep_count % 30:
                print('saving...   ', rep_count)
                with open(f'lyrics.pkl', 'wb') as f:
                    pickle.dump(lyrs, f, pickle.HIGHEST_PROTOCOL)
            continue


        try:
            lyrs[s] = g.lyrics(song_url=f'https://genius.com/{query}-lyrics')
        except:
            print(f'https://genius.com/{query}-lyrics')
            continue
            lyrs[s] = manual_retrieval()

        if ind % 100 == 0:
            with open(f'lyrics.pkl', 'wb') as f:
                pickle.dump(lyrs, f, pickle.HIGHEST_PROTOCOL)
        if ind % 500 == 0:
            count += 1
            with open(f'lyr_backup_{count}', 'wb') as f:
                pickle.dump(lyrs, f, pickle.HIGHEST_PROTOCOL)

get_lyrics(True)

lyrs = load_obj('lyrics')

print()
