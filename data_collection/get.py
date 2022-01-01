import re
import os
import sys
import time
import random
sys.path.append('../')
import pickle
import spotipy
import lyricsgenius
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials


def load_obj(datatype):
    with open(f"{datatype}" + '.pkl', 'rb') as f:
        return pickle.load(f)


class Query:
    def __init__(self, storage, commit):
        self.storage = storage  # maybe handle storage ops outside of this class
        self.commit = commit
        self.spotipy = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="fcc7b07104154ff29db823936cc41236",
                                                                        client_secret="00b43d603ff64b388e3f913016fa5018"))
        self.lyr_g = lyricsgenius.Genius("Y2p-Qam6OpCix8jgS1KHq5SUe85dxdZ_LCBVdz5pOsb2gcCL1btUNsgr6iWAO5Wl")

    def __getitem__(self, items):
        if type(items) == list:
            self.from_names(items)
        else:
            self.from_names([items])

    def get(self):  # make sure redundant searches arent performed
        lyrics, discrete, continuous, names = [], [], [], []
        tracks, temp = [], []
        for ind, song in enumerate(tracks):
            print(ind, song['name'])
            data = self.storage.get(song['name'], {})
            names.append(song['name'])
            if not data['Raw_Lyrics']:
                lyrics.append(self.get_lyrics(song['artists'][0]['name'], song['name']))
            else:
                lyrics.append(self.storage[song['name']]['Raw_Lyrics'])

            if not data['Discrete_Data']:
                discrete.append(self.spotipy.audio_analysis(song['id']))
                temp.append(False)
            else:
                discrete.append(self.storage[song['name']]['Discrete_Data'])
                temp.append(True)

            if ind and ind % 100 == 0:
                search = [track['id'] for track, got in zip(tracks[ind-100:ind], temp) if not got]
                feats = self.spotipy.audio_features(search)

                [continuous.append(self.storage[song['name']]['Continuous_Data']) if got
                 else continuous.append(feats[search.index(track['id'])]) for track, got in zip(tracks[ind-100:ind], temp)]

                self.commit(zip(names, lyrics, continuous, discrete, tracks[ind-100:ind]))


    def from_names(self, names):  # implement repairing
        tracks = []
        for item in names:
            if not item or type(item) == str:
                if self.storage.get(item, {}).get('Meta_Data'):
                    tracks.append(self.storage[item]['Meta_Data'])
                    continue
                query = f'track:{item}'
                temp = self.spotipy.search(query, limit=1, offset=0, type='track')['tracks']['items']
                if temp:
                    tracks.append(temp[0])
            else:
                tracks.append(item)
        return tracks


    def from_playlist(self, id):
        offset = 0
        tracks = items = [track['track'] for track in self.spotipy.playlist_tracks(id, offset=offset)['items']]
        while len(items) == 100:
            offset += 100
            items = [track['track'] for track in self.spotipy.playlist_tracks(id, offset=offset)['items']]
            tracks += items
        return tracks


    def get_lyrics(self, artist, song):
        temp = random.randint(0,15)/10
        if temp < .5:
            temp = random.randint(0, 12)/10
        time.sleep(temp)

        a = artist[0] + artist[1:].lower()
        s = re.sub(r'\sfeat.*', '', re.sub(r'\s\(feat.*\)', '', song)).lower()
        for char in '.\'’,!?()[]$&\\/\"':
            s = s.replace(char, '')
            a = a.replace(char, '')
        query = f'{a}-{s}'.replace(" ", "-")
        try:
            return self.lyr_g.lyrics(song_url=f'https://genius.com/{query}-lyrics')
        except:
            search = self.lyr_g.search_songs(query)
            if search['hits']:
                return self.lyr_g.lyrics(song_url=search['hits'][0]['result']['url'])
        return None

#     new[k] = {'Raw_Lyrics': lyrs.get(k, None), 'Continuous_Data': rep.get(k, None)[1], 'Discrete_Data': temp, 'Meta_Data': rep.get(k, None)[0]}