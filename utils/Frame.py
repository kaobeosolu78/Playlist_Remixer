from data_collection.get import Query
import sys
sys.path.append('../')
import pickle
import json
from analysis.LyricalAnalysis import LyricalAnalysis
from analysis.TonalAnalysis import TonalAnalysis
from utils.SongData import SongData
from utils.SongStream import SongStream
from utils.Posture import AuditoryBody

def load_obj(datatype):
    with open(f"{datatype}" + '.pkl', 'rb') as f:
        return pickle.load(f)


class Frame(SongData, Query):  # only pass values that need to be searched for thru

    def __init__(self, id=None, tracknames=None, spotify_id=None):
        # self = super(Frame, cls).__new__(cls)
        with open('existing_frames.json') as f:
            self.existing_frames = json.load(f)
        if id:
            self.current_slice = self.existing_frames[id]
        else:
            SongData.__init__(self)
            Query.__init__(self, self.pickled_data, self.commit)

            if spotify_id:
                tracks = self.from_playlist(self, spotify_id)
            else:
                req = [self.pickled_data[song].get('Meta_Data', None) if self.pickled_data.get(song, False)
                       else song for song in tracknames]
                tracks = self.from_names(req)

            self.current_slice = {'id': ''.join([char[:3] if len(char) > 3 else 'aaa' for char in
                                      sorted([track['name'] for track in tracks])[:4]]).replace(' ', ''),
                                      'tracknames': [track['name'] for track in tracks],
                                      'spotify_id': spotify_id}

            self.existing_frames[self.current_slice['id']] = self.current_slice
            with open(f'existing_frames.json', "w") as f:
                json.dump(self.existing_frames, f)

    def create(self):
        pass

    # def __call__(self, tracknames):
    #     for song in tracknames:
    #     # if song not in self.current_slice.tracknames:
    #
    #     AuditoryBody()
    #     return

    # @classmethod
    # def create_body(cls, instance):
    #
    #     return AuditoryBody(instance, lyrical_analysis, tonal_analysis)

db = SongData()
test = list(db.pickled_data.keys())[:100]
temp = Frame(tracknames=test)

print()
