import sys
sys.path.append('../')
import pickle
from utils.SongData import SongData

def load_obj(datatype):
    with open(f"{datatype}" + '.pkl', 'rb') as f:
        return pickle.load(f)

class TonalAnalysis(SongData):
    def __init__(self, data_slice):
        self.feats = self.construct_feats(data_slice)

    def construct_feats(self, data_slice):
        pass


print()