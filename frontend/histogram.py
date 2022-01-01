import sys
import matplotlib
from mainwin import MainWindow
matplotlib.use('Qt5Agg')
sys.path.append('../')
from utils.SongStream import SongStream
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QGridLayout, QLabel, QWidget, QPushButton, QLineEdit, QAction, \
    QCalendarWidget, QErrorMessage, QListWidget, QAbstractItemView, QSlider, QCheckBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure




class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=11, height=11, dpi=80):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class Histograms(MainWindow):

    def __init__(self):
        super(Histograms, self).__init__()

        self.bundle = self.get_bundle()
        self.plt = self.plot()
        self.grid.addWidget(self.plt, 0, 1)
        self.add_list()

        self.finish('hist')

    # def add_lb(self):
    #
    # def add_button(self):
    #

    def get_bundle(self):
        ss = SongStream()
        moving_avg = ss.mov_avg(window=10, units='days')
        pack = moving_avg.bundle(num_common=10) # most common
        return pack

    def add_list(self):
        def add_items(self, lw):
            for frame in self.bundle.keys():
                lw.addItem(frame)
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.itemClicked.connect(lambda: self.new_plot())
        self.grid.addWidget(self.list_widget, 0, 0, 2, 1)
        add_items(self, self.list_widget)

    def plot(self, frame=None):
        sc = MplCanvas(self, width=11, height=11, dpi=80)
        if not frame:
            temp = self.bundle[list(self.bundle.keys())[0]]
        else:
            temp = self.bundle[frame]

        n, bins, patches = sc.axes.hist(temp.freq)
        sc.axes.set_xticks(bins[:len(bins) - 1])
        sc.axes.set_xticklabels([name[:12] if len(name) > 12 else name for name in temp.body.tracknames], rotation=90)
        return sc

    def new_plot(self):
        self.grid.removeWidget(self.plt)
        self.plt = self.plot(self.list_widget.currentItem().text())
        self.grid.addWidget(self.plt, 0, 1)


def main():
    app = QApplication(sys.argv)
    a = Histograms()
    sys.exit(app.exec_())

main()

