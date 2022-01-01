import re
# from nltk.corpus import stopwords
import nltk


class SongLyrics:
    def __init__(self, name, lyrs, pool):
        self.pool = pool
        self.name = name
        if lyrs:
            self.lyrics = self.process_lyrics(lyrs)
        else:
            self.lyrics = None

    def __bool__(self):
        return bool(self.lyrics)

    def process_lyrics(self, lyrs): # mess around with punctuation, add stopwords
        # sw = stopwords.words('english')
        lyrs = lyrs.lower()
        for sw in ['.', '(', ')', ',']:
            lyrs = lyrs.replace(sw, '')
        temp = re.sub(r'\[.*\]\n', '', lyrs)
        return type('Lyrics', (object,), {'words': temp.replace('\n', ' ').split(' '),
                                    'bars': temp.split('\n'), 'all': lyrs})

    def personality(self, threshold=1):
        # gets the words unique to this song from the la pool
        unique_words = []
        distribution = dict(self.pool.frequency_dist)
        for word in self.lyrics.words:
            freq = distribution.get(word, 0)
            if freq < threshold and word not in [val[0] for val in unique_words] and word != '':
                unique_words.append((word, freq))
        length_factor = self.pool.avg_length/len(self.lyrics.all)
        return (unique_words, len(unique_words)*length_factor)

    @property
    def hook(self):
        # grabs the hook by looking for repeated lines
        dist = nltk.FreqDist(self.lyrics.bars).most_common()
        for k in range(len(dist)-1):
            if dist[k][1] < 2:
                break
        dem_hook = [b[0] for b in dist[:k]]

        hook, count = [], 0
        for bar in self.lyrics.bars:
            if bar in dem_hook:
                hook.append(bar)
                count += 1
            if count == len(dem_hook):
                break
        return hook
