from PyQt5.QtWidgets import QMainWindow, QApplication, QGridLayout, QLabel, QWidget, QPushButton, QLineEdit, QAction, \
    QCalendarWidget, QListWidget
from PyQt5.QtCore import QDate
# from playlist_remixer_v3 import Remixer
from mainwin import MainWindow
import sys
from utils.SongStream import SongStream
from utils.SongData import SongData
from dateutil.parser import parse
from utils.Posture import AuditoryBody
import pickle

def load_obj(datatype):
    with open(f"{datatype}" + '.pkl', 'rb') as f:
        return pickle.load(f)

class DayData(MainWindow):
    # data about songs played on day selected from calendar
    def __init__(self, date, songstream):
        super().__init__()
        self.date = date
        self.ss = songstream
        self.sd = SongData()
        self.todays_songs = self.get_day_songs()
        self.averages = self.get_avgs()
        self.ab = AuditoryBody([song['trackName'] for song in self.todays_songs], self.sd)
        self.add_labels()
        self.finish(self.date.strftime('%b, %d %Y'))

    def get_day_songs(self):
        # get songs played on this day
        return [song for song in self.ss if parse(song['endTime']).date() == self.date]

    def add_button(self):
        self.connect_rem = QPushButton()
        self.button.clicked.connect(self.connect)
        self.grid.addWidget(self.connect_rem, 10, 0)

    def add_labels(self):
        # add labels to popup
        self.lw = QListWidget()
        for song in self.todays_songs:
            self.lw.addItem(song['trackName']),
        self.grid.addWidget(self.lw, 0, 0, 9, 1)
        self.grid.addWidget(QLabel('Day Average Values'), 0, 1)
        for ind, (att, avg) in enumerate(self.averages.items()):
            self.grid.addWidget(QLabel(att), ind+1, 1)
            self.grid.addWidget(QLabel(str(avg)), ind+1, 2)
        self.grid.addWidget(QLabel('Average Song Length'), ind+2, 1)
        self.grid.addWidget(QLabel(str(self.ab.la.avg_length)), ind+2, 2)

    def get_avgs(self):
        # gets average continuous var values for labels
        mean_dic = {val: 0 for val in ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']}
        for song in self.todays_songs:
            for att in mean_dic.keys():
                mean_dic[att] += self.sd.pickled_data[song['trackName']]['Continuous_Data'][att]
        for att in mean_dic.keys():
            mean_dic[att] = mean_dic[att]/len(self.todays_songs)
        return mean_dic

    def connect(self):
        pass

class Calendar(MainWindow):
    def __init__(self):
        super().__init__()
        self.ss = SongStream()
        self.setup_cal()


        self.finish('Calendar', x_dim=600, y_dim=500)

    def setup_cal(self):
        self.calendar = QCalendarWidget(self)
        self.calendar.setDateRange(QDate(parse(list(self.ss)[len(list(self.ss))-1]['endTime']).year, parse(list(self.ss)[len(list(self.ss))-1]['endTime']).month, parse(list(self.ss)[len(list(self.ss))-1]['endTime']).day),
                                   QDate(parse(list(self.ss)[0]['endTime']).year, parse(list(self.ss)[0]['endTime']).month, parse(list(self.ss)[0]['endTime']).day))

        self.grid.addWidget(self.calendar, 0, 0)
        self.calendar.clicked.connect(self.date_search)

    def date_search(self):
        self.temp = DayData(self.calendar.selectedDate().toPyDate(), self.ss)


def main():
    app = QApplication(sys.argv)
    a = Calendar()
    sys.exit(app.exec_())

main()

