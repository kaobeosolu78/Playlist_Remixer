from PyQt5.QtWidgets import QMainWindow, QApplication, QGridLayout, QLabel, QWidget, QPushButton, QLineEdit, QAction, \
    QCalendarWidget, QErrorMessage, QListWidget, QAbstractItemView, QSlider, QCheckBox
from collections import namedtuple
from qtrangeslider import QRangeSlider
from operator import itemgetter
from statistics import mean
import pickle
import sys
from mainwin import MainWindow
sys.path.append('../')
import sys
from utils.SongData import SongData
from utils.Playlist import Playlist
# add word length slider


def load_obj(datatype):
    with open(f"{datatype}" + '.pkl', 'rb') as f:
        return pickle.load(f)


class SortedData(dict):
    def __init__(self, db, names):
        self.db = db
        self.names = names
        for val in ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']:
            self[val] = []
        Song = namedtuple('Song', 'key name value')
        for song in names:
            for att in self.keys():
                if db.pickled_data.get(song, None):
                    self[att].append((song, db.pickled_data[song]['Continuous_Data'][att]))
        for att in self.keys():
            self[att] = [Song(ind, val[0], val[1]) for ind, val in enumerate(sorted(self[att], key=itemgetter(1)))]

    @property
    def mean_vals(self):
        mean_val = {att: 0 for att in self.keys()}
        for att in mean_val.keys():
            mean_val[att] = mean([s.value for s in self[att]])
            for song in self[att]:
                if song.value > mean_val[att]:
                    mean_val[att] = song.key
                    break
        return mean_val

    def all_values(self, att):
        return [song.value for song in self[att]]

    def from_val(self, val, att):
        return self.all_values(att).index(min(self.all_values(att), key=lambda x:abs(x-val)))

class Remixer(MainWindow):
    def __init__(self, tracknames=None):
        super().__init__()
        Attrib = namedtuple('Attrib', 'slider checkbox')
        self.attrs = {att: Attrib(QRangeSlider(), QCheckBox()) for att in ['danceability', 'energy', 'speechiness',
                                                               'acousticness', 'instrumentalness', 'liveness',
                                                               'valence']}
        self.db = SongData()
        self.tracknames = list(Playlist(id='ZV3AGAWA').names)
        if tracknames:
            self.tracknames = tracknames
        self.add_button()
        self.add_list()
        self.sorted_data = SortedData(self.db, self.tracknames)
        self.add_songs(self.tracknames)
        self.add_sliders()
        self.update_list()
        self.finish('Playlist Remixer')

    def add_button(self):
        self.button = QPushButton('Submit.')
        self.button.clicked.connect(self.update_list)
        self.grid.addWidget(self.button, 3, 0)

    def add_list(self):
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_widget.itemClicked.connect(lambda: self.like_this())
        self.grid.addWidget(self.list_widget, 1, 0, 2, 1)

    def add_songs(self, songs):
        [self.list_widget.removeItemWidget(self.list_widget.item(ind)) for ind in range(self.list_widget.count()) if self.list_widget.item(ind).text() not in songs]
        for ind, val in enumerate(songs):
            self.list_widget.insertItem(ind, val)

    def like_this(self):
        def avg_selected_vals(self):
            mean_dict = {att: 0 for att in ['danceability', 'energy', 'speechiness', 'acousticness',
                                       'instrumentalness', 'liveness', 'valence']}
            for item in self.list_widget.selectedItems():
                data = self.db.pickled_data[item.text()]['Continuous_Data']
                for att in mean_dict:
                    mean_dict[att] += data[att]
            for key in mean_dict.keys():
                mean_dict[key]/len(self.list_widget.selectedItems())
            return mean_dict
        comparison_vals = avg_selected_vals(self)
        for att, val in comparison_vals.items():
            self.attrs[att].slider.setValue(
                [self.sorted_data.from_val(val, att) - int(len(self.sorted_data['energy'])*.15),
                 self.sorted_data.from_val(val, att) + int(len(self.sorted_data['energy'])*.15)])
        self.update_list()

    def add_sliders(self):
        mean_song_names = self.sorted_data.mean_vals
        slider_range = int(len(self.sorted_data['energy'])*.15)
        for ind, att in enumerate(self.attrs.keys()):
            self.attrs[att].slider.setMinimum(0)
            self.attrs[att].slider.setMaximum(len(self.sorted_data['energy'])-1)
            self.attrs[att].slider.setValue([mean_song_names[att]-slider_range, mean_song_names[att]+slider_range])
            self.attrs[att].slider.sliderReleased.connect(lambda: self.update_list)
            self.grid.addWidget(self.attrs[att].slider, 1, ind + 2)
            # self.attrs[att].checkbox.setChecked(True)
            self.grid.addWidget(self.attrs[att].checkbox, 2, ind+2)

            self.grid.addWidget(QLabel(att), 0, ind + 2)

    def update_list(self):
        product = []
        for song in [s for s in self.tracknames if self.db.pickled_data.get(s, None)]:
            count = 0
            for att, vals in [(att, data.slider.sliderPosition()) for att, data in self.attrs.items() if data[1].isChecked()]:
                if self.db.pickled_data[song]['Continuous_Data'][att] > self.db.pickled_data[self.sorted_data[att][int(vals[0])].name]['Continuous_Data'][att] and \
                        self.db.pickled_data[song]['Continuous_Data'][att] < self.db.pickled_data[self.sorted_data[att][int(vals[1])].name]['Continuous_Data'][att]:
                    count += 1
                    print(count)
                    continue
                else:
                    break
            if count == len([att for att, data in self.attrs.items() if data[1].isChecked()]):
                product.append(song)
        self.add_songs(product)


def main():
    app = QApplication(sys.argv)
    a = Remixer()
    sys.exit(app.exec_())

main()