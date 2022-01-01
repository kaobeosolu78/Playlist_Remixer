import pickle
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import sys



def load_obj(datatype):
    with open(f"{datatype}" + '.pkl', 'rb') as f:
        return pickle.load(f)


class Playlist:
    def __init__(self, id=None, sp_id=None):
        self.spotipy = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="fcc7b07104154ff29db823936cc41236",
                                                                        client_secret="00b43d603ff64b388e3f913016fa5018"))
        if id:
            self.id = id
            self.playlist = load_obj(id)
        elif sp_id:
            self.playlist = self.load_pl(sp_id)
            self.id = ''.join([song['track']['name'][:1] for song in self.playlist[:8]])
            with open(f'{self.id}.pkl', "wb") as f:
                pickle.dump(self.playlist, f, pickle.HIGHEST_PROTOCOL)
        else:
            pass

    @property
    def names(self):
        for item in self.playlist:
            yield item['track']['name']

    def load_pl(self, pl_id):
        offset = 0
        tracks = items = [track for track in self.spotipy.playlist_tracks(pl_id, offset=offset)['items']]
        while len(items) == 100:
            offset += 100
            items = [track for track in self.spotipy.playlist_tracks(pl_id, offset=offset)['items']]
            tracks += items
        return tracks

temp = Playlist(sp_id='2RJeNQGAgdmIMKiIKrFx8G')

print()