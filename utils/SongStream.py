import sys
sys.path.append('../')
from utils.SongData import SongData
from matplotlib import pyplot
import json
import datetime
from collections import Counter, namedtuple
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from utils.Posture import AuditoryBody

def date_range(start, end, delta):
    current = start
    if not isinstance(delta, datetime.timedelta):
        delta = relativedelta(**delta)
    while current < end:
        yield current
        current += delta


class MovingAverage:
    def __init__(self, product, window):
        self.histogram = {name: Counter(val) for name, val in product.items()}
        self.window = window
        self.db = SongData()

    def bundle(self, num_common):
        bundle = namedtuple('bundle', 'body freq')
        product = {}
        for date, slice in self.histogram.items():
            product[date] = bundle(AuditoryBody([val[0] for val in slice.most_common(num_common)], self.db), [val[1] for val in slice.most_common(num_common)])
        return product

    def histogram_plot(self):
        pyplot.hist()
        pyplot.show()

class SongStream(SongData):
    def __init__(self):
        super().__init__()
        self.history = [song for k in range(3) for song in json.load(open(f'/home/kaobe/Desktop/Programming_Projects/Python/spot_avg/venv/include/temp/StreamingHistory{k}.json'))]
        self.history = self.filter_skips()

    def __iter__(self):
        for song in self.history:
            if not self.pickled_data.get(song['trackName'], None):
                continue
            yield song

    def filter_skips(self, threshold=0.9):
        return [song for song in self if (self.pickled_data[song['trackName']]['Meta_Data']['duration_ms'] -
                    song['msPlayed'])/self.pickled_data[song['trackName']]['Meta_Data']['duration_ms'] < threshold]

    def mov_avg(self, window=7, units='days'):
        td = {'days': datetime.timedelta(days=window), 'hours': datetime.timedelta(hours=window)}

        data = self.filter_skips()
        product = {f'{rng.strftime("%m/%d/%Y, %H:%M:%S")}-{(rng+td[units]).strftime("%m/%d/%Y, %H:%M:%S")}': []
                   for rng in date_range(parse(data[0]['endTime']), parse(data[len(data)-1]['endTime']), td[units])}
        prod_ind = 0
        for song in data:
            listen_date = parse(song['endTime']) #-datetime.timedelta(milliseconds=)
            if listen_date > datetime.datetime.strptime((list(product.keys())[prod_ind]).split('-')[1], "%m/%d/%Y, %H:%M:%S"):
                prod_ind += 1
            else:
                product[list(product.keys())[prod_ind]].append(song['trackName'])  # determine here what type of data to analyze
        return MovingAverage(product, window)


