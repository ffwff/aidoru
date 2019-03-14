from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from operator import attrgetter
import src.MainWindow as MainWindow
from .PlayingAlbumView import PlayingAlbumView

# file list view
class FileListTableItemDelegate(QStyledItemDelegate):

    def sizeHint(self, option, index):
        size = QStyledItemDelegate.sizeHint(self, option, index)
        size = QSize(size.width(), max(size.height(), 40))
        return size

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

        self.setMouseTracking(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setHorizontalHeaderLabels(["Duration", "Name", "Artist", "Album", "Album artist", "Year", ""])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # dur
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents) # year
        self.horizontalHeader().sectionClicked.connect(self.headerClicked)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers);
        self.setShowGrid(False)
        self.setItemDelegate(FileListTableItemDelegate())

        self.hoverRow = -1
        self.nrows = 0
        self.mediaRow = []
        self.sortKey = None
        self.sortRev = False

    def selectPlaying(self):
        if not self.mediaRow: return
        try:
            i, _ = next(filter(lambda i: i[1] == MainWindow.instance.mediaInfo, enumerate(self.mediaRow)))
            self.selectRow(i)
        except StopIteration:
            pass

    # add item
    def addMedia(self, mediaInfo, append=True):
        if not mediaInfo: return
        self.setRowCount(self.nrows+1)
        self.setItem(self.nrows, 0, QTableWidgetItem(mediaInfo.duration.strftime("%M:%S")))
        self.setItem(self.nrows, 1, QTableWidgetItem(mediaInfo.title))
        self.setItem(self.nrows, 2, QTableWidgetItem(mediaInfo.artist))
        self.setItem(self.nrows, 3, QTableWidgetItem(mediaInfo.album))
        self.setItem(self.nrows, 4, QTableWidgetItem(mediaInfo.albumArtist))
        self.setItem(self.nrows, 5, QTableWidgetItem(str(mediaInfo.year) if mediaInfo.year != -1 else ""))
        self.setItem(self.nrows, 6, QTableWidgetItem("")) # filler
        #self.resizeRowToContents(self.nrows)
        if append: self.mediaRow.append(mediaInfo)
        self.nrows += 1

    def mediasAdded(self, medias, append=True):
        for media in medias:
            self.addMedia(media, append)
        self.resizeRowsToContents()

    # events
    def headerClicked(self, index):
        if index == 0: key = 'duration'
        elif index == 1: key = 'title'
        elif index == 2: key = 'artist'
        elif index == 3: key = 'album'
        elif index == 4: key = 'albumArtist'
        elif index == 5: key = 'year'
        else: return
        if key == self.sortKey:
            self.sortRev = not self.sortRev

        else:
            self.sortKey = key
            self.sortAsc = False
        self.mediaRow = sorted(MainWindow.instance.medias, key=attrgetter(key), reverse=self.sortRev)
        self.clearContents()
        self.nrows = 0
        self.mediasAdded(self.mediaRow, False)
        self.selectPlaying()

    def mouseMoveEvent(self, e):
        QTableWidget.mouseMoveEvent(self, e)
        index = self.indexAt(e.pos())
        if index.column() == self.columnCount()-1:
            self.hoverRow = -1
        else:
            self.hoverRow = index.row()

    def leaveEvent(self, e):
        self.hoverRow = -1

    def mousePressEvent(self, e):
        QTableWidget.mousePressEvent(self, e)
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
        tableWidget.setAlternatingRowColors(True)
        vboxLayout.addWidget(tableWidget)

        mainWindow = MainWindow.instance
        if mainWindow.medias:
            self.tableWidget.mediasAdded(mainWindow.medias)
            self.tableWidget.selectPlaying()

    def bindEvents(self):
        MainWindow.instance.mediasAdded.connect(self.tableWidget.mediasAdded)
        MainWindow.instance.songInfoChanged.connect(self.tableWidget.selectPlaying)
