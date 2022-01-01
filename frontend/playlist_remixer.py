from PyQt5.QtWidgets import QMainWindow, QApplication, QGridLayout, QLabel, QWidget, QPushButton, QLineEdit, QAction, \
    QCalendarWidget, QErrorMessage, QListWidget, QAbstractItemView, QSlider, QCheckBox
from sklearn.preprocessing import normalize
from PyQt5 import QtCore, QtGui
from mainwin import MainWindow
import numpy as np
import pickle
import math
import sys
sys.path.append('../')
from utils.SongData import SongData
from utils import Posture

# liveness+instrumentalness -binary

def load_obj(datatype):
    with open(f"{datatype}" + '.pkl', 'rb') as f:
        return pickle.load(f)


class Main(MainWindow):
    def __init__(self):
        super().__init__()

        self.db = SongData()
        # self.temp = load_obj('../feature_repository')
        self.song_database = load_obj('../playlist_feats')
        self.playlist = load_obj('../playlist')

        self.values = {val: [QSlider(), QCheckBox()] for val in ['danceability', 'energy', 'key', 'loudness', 'speechiness', 'acousticness',
                                     'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']}

        self.raw_features = np.array([[item[1][att] for item in self.song_database] for att in self.values.keys()])

        self.init_values()
        self.add_list_wid()
        self.update_list({name: self.raw_features[list(self.values.keys()).index(name)].mean() for name in self.values.keys()})
        self.finish('playlist_remixer')


    def add_list_wid(self):
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_widget.itemClicked.connect(lambda: self.like_this())
        self.grid.addWidget(self.list_widget, 1, 0, 2, 1)

    def like_this(self):
        for key, options in self.values.items():
            options[0].setValue(int(self.temp[self.list_widget.currentItem().text()][1][key]*100000))
        self.update_list(False)

    def init_values(self):
        for ind, name in enumerate(list(self.values.keys())): # generator
            self.values[name][0].setMinimum(int(self.raw_features[ind].min()*100000))
            self.values[name][0].setMaximum(int(self.raw_features[ind].max()*100000))
            self.values[name][0].setValue(int(self.raw_features[ind].mean()*100000))
            self.values[name][0].sliderReleased.connect(lambda: self.update_list(False))
            self.grid.addWidget(self.values[name][0], 1, ind + 2)

            self.values[name][1].toggled.connect(lambda: self.update_list(False))
            self.grid.addWidget(self.values[name][1], 2, ind+2)

            self.grid.addWidget(QLabel(name), 0, ind + 2)
        self.button = QPushButton('Submit')
        self.button.clicked.connect(self.submit)
        self.grid.addWidget(self.button, 3, 0)

    def submit(self):
        with open(f'../posture.pkl', 'wb') as f:
            post = Posture([self.list_widget.item(k).data(0) for k in range(self.list_widget.count())],
                           {name: slider[0].value()/100000 for name, slider in self.values.items() if slider[1].isChecked()})
            pickle.dump(post, f, pickle.HIGHEST_PROTOCOL)

    def update_list(self, data=None):
        if not data:
            data = {name: slider[0].value() / 100000 for name, slider in self.values.items()}
        self.add_songs(self.get_similair_songs(data))

    def add_songs(self, songs):
        self.list_widget.clear()
        for ind, val in enumerate(songs):
            self.list_widget.insertItem(ind, val)

    def get_similair_songs(self, values):
        # add storage for indexes to cut down on loops
        # sort
        if not sum([val[1].isChecked() for val in self.values.values()]):
            return []

        sorted_indexes = [self.raw_features[ind].argsort() for ind in range(len(self.values))]
        # returns the sorted_index of the selected value
        def get_sorted_index(feat_ind, feat):
            song_ind = 0
            while song_ind != len(sorted_indexes[feat_ind]):
                if self.raw_features[feat_ind][sorted_indexes[feat_ind][song_ind]] > values[feat]:
                    return song_ind
                song_ind += 1

        product = set()
        window = 1
        sorted_index_storage = [get_sorted_index(feat_ind, feat) for feat_ind, feat in enumerate(self.values.keys())]
        while len(product) < 15:
            temp = [set() for _ in range(len(sorted_indexes))]
            for feat_ind, feat in enumerate(self.values.keys()):
                if not self.values[feat][1].isChecked():
                    continue

                song_ind = sorted_index_storage[feat_ind]
                try:
                    [temp[feat_ind].add(sorted_indexes[feat_ind][add_ind])
                     for add_ind in range(song_ind-window+1, song_ind+window) if 0 <= add_ind <= len(sorted_indexes[feat_ind])-1]
                except:
                    print()
            product = product | set.intersection(*[temp[ind] for ind, options in enumerate(self.values.values()) if options[1].isChecked()])
            window += 1

        return [self.song_database[ind][0]['name'] for ind in product]

def main():
    app = QApplication(sys.argv)
    a = Main()
    sys.exit(app.exec_())

main()


