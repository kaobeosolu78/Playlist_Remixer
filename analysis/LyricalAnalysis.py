import pickle
import nltk
from analysis.SongLyrics import SongLyrics
from unidecode import unidecode
from nltk.corpus import stopwords


def load_obj(datatype):
    with open(f"{datatype}" + '.pkl', 'rb') as f:
        return pickle.load(f)


class LyricalAnalysis:
    def __init__(self, data_slice):
        # splits pool into dict of SongLyric objects
        self.songs = {name: SongLyrics(name, unidecode(lyrs), self) for name, lyrs in data_slice if lyrs}
        print()

    @property
    def avg_length(self):
        # average song length
        if not hasattr(self, '_avg_length'):
            self._avg_length = sum([len(song.lyrics.all) for song in self.songs.values()]) / len(self.songs)
        return self._avg_length

    def get_frequency_dist(self, exclude=[None]):
        # nltk frequence dist, word occurrences
        if not hasattr(self, '_freq_dist'):
            all_lyrics = ' '.join([song.lyrics.all for song in self.songs.values() if song not in exclude]).replace('\n', ' ')
            self._freq_dist = nltk.FreqDist(nltk.word_tokenize(all_lyrics))
        return self._freq_dist
    frequency_dist = property(get_frequency_dist)

    def lyrical_fingerprints(self):
        # iter for words that make each song unique
        for song in self.songs:
            yield song.personality()



# pl = LyricalFeatures()
# print(pl.avg_length)
# for song, item in pl.songs.items():
#     print(song, item.lyrical_personality())