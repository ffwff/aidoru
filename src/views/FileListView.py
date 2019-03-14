from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from operator import attrgetter
import src.MainWindow as MainWindow
from .PlayingAlbumView import PlayingAlbumView

# file list view
class FileListTableItemDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):
        option.state &= ~QStyle.State_HasFocus
        if option.styleObject.hoverRow == index.row():
            option.state |= QStyle.State_MouseOver
        elif index.column() == option.styleObject.columnCount()-1:
            option.state &= ~QStyle.State_MouseOver
        QStyledItemDelegate.paint(self, painter, option, index)

class FileListTableWidget(QTableWidget):
    # https://github.com/lowbees/Hover-entire-row-of-QTableView
    def __init__(self, rows=1, cols=7):
        QTableView.__init__(self, rows, cols)
        self.setStyleSheet("""
""")
        self.setMouseTracking(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #self.horizontalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(["Duration", "Name", "Artist", "Album", "Album artist", "Year", ""])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # dur
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents) # year
        self.horizontalHeader().sectionClicked.connect(self.headerClicked)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers);
        self.setShowGrid(False)

        self.hoverRow = -1
        self.setItemDelegate(FileListTableItemDelegate())
        self.nrows = 0
        self.mediaRow = []

    # add item
    def addMedia(self, mediaInfo):
        self.setRowCount(self.nrows+1)
        self.setItem(self.nrows, 0, QTableWidgetItem(mediaInfo.duration.strftime("%M:%S")))
        self.setItem(self.nrows, 1, QTableWidgetItem(mediaInfo.title))
        self.setItem(self.nrows, 2, QTableWidgetItem(mediaInfo.artist))
        self.setItem(self.nrows, 3, QTableWidgetItem(mediaInfo.album))
        self.setItem(self.nrows, 4, QTableWidgetItem(mediaInfo.albumArtist))
        self.setItem(self.nrows, 5, QTableWidgetItem(str(mediaInfo.year) if mediaInfo.year != -1 else ""))
        self.setItem(self.nrows, 6, QTableWidgetItem("")) # filler
        self.resizeRowToContents(self.nrows)
        self.mediaRow.append(mediaInfo)
        self.nrows += 1

    # events
    def headerClicked(self, index):
        if index == 0: key = attrgetter('duration')
        elif index == 1: key = attrgetter('title')
        elif index == 2: key = attrgetter('artist')
        elif index == 3: key = attrgetter('album')
        elif index == 4: key = attrgetter('albumArtist')
        elif index == 5: key = attrgetter('year')
        self.mediaRow.sort(key=key)

    def mouseMoveEvent(self, e):
        QTableView.mouseMoveEvent(self, e)
        index = self.indexAt(e.pos())
        if index.column() == self.columnCount()-1:
            self.hoverRow = -1
        else:
            self.hoverRow = index.row()

    def mousePressEvent(self, e):
        QTableView.mousePressEvent(self, e)
        index = self.indexAt(e.pos())
        mainWindow = MainWindow.instance
        if self.mediaRow:
            if mainWindow.mediaInfo and self.mediaRow[index.row()] == mainWindow.mediaInfo:
                return
            mainWindow.setSong(self.mediaRow[index.row()].path)


class FileListView(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.initUI()
        self.bindEvents()

    def initUI(self):
        vboxLayout = QVBoxLayout()
        self.setLayout(vboxLayout)

        self.tableWidget = tableWidget = FileListTableWidget()
        vboxLayout.addWidget(tableWidget)

        mainWindow = MainWindow.instance

        if mainWindow.medias:
            class PopulateMediaThread(QThread):

                def run(self_):
                    for media in mainWindow.medias:
                        self.tableWidget.addMedia(media)
                    self.tableWidget.resizeRowsToContents()
                    del self._thread

            self._thread = PopulateMediaThread()
            self._thread.start()

    def bindEvents(self):
        MainWindow.instance.mediaAdded.connect(self.tableWidget.addMedia)
