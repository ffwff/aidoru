from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from operator import attrgetter
from .PlayingAlbumView import PlayingAlbumView
from .SearchView import SearchView
from src.Application import Application
from src.utils import dropShadow, highlightText
import re

FILTER_REGEX = re.compile(r'\b(artist|album|aartist)\:"((?:[^"\\]|\\.)*)"', re.IGNORECASE)

# file list view
class FileListTableItemDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):
        option.state &= ~QStyle.State_HasFocus
        option.state &= ~QStyle.State_MouseOver
        if option.styleObject.hoverRow == index.row():
            option.state |= QStyle.State_MouseOver
        QStyledItemDelegate.paint(self, painter, option, index)

class FileListTableWidget(QTableWidget):
    # https://github.com/lowbees/Hover-entire-row-of-QTableView
    def __init__(self, rows=1, cols=7):
        QTableView.__init__(self, rows, cols)

        self.setMouseTracking(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setHorizontalHeaderLabels(["Time", "Name", "Artist", "Album", "Album artist", "Year", ""])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # dur
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents) # year
        self.horizontalHeader().setGraphicsEffect(dropShadow())
        self.horizontalHeader().sectionClicked.connect(self.headerClicked)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers);
        self.setShowGrid(False)
        self.setItemDelegate(FileListTableItemDelegate())

        self.hoverRow = -1
        self.nrows = 0
        self.sortKey = "title"
        self.sortRev = False
        self.filterText = ""
        self.specialFilter = False
        self.mediaRow = []
        
        self.mediaBatch = 0

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def selectPlaying(self):
        if not self.mediaRow: return
        try:
            i, _ = next(filter(lambda i: i[1] == Application.mainWindow.mediaInfo, enumerate(self.mediaRow)))
            self.selectRow(i)
        except StopIteration:
            pass

    # add item
    def addMedia(self, mediaInfo, highlight=None):
        if not mediaInfo: return
        self.setRowCount(self.nrows+1)
        self.setItem(self.nrows, 0, QTableWidgetItem(mediaInfo.duration.strftime("%M:%S")))
        if highlight:
            self.setCellWidget(self.nrows, 1, QLabel(highlightText(mediaInfo.title, highlight)))
        else:
            self.setItem(self.nrows, 1, QTableWidgetItem(mediaInfo.title))
        self.setItem(self.nrows, 2, QTableWidgetItem(mediaInfo.artist))
        self.setItem(self.nrows, 3, QTableWidgetItem(mediaInfo.album))
        self.setItem(self.nrows, 4, QTableWidgetItem(mediaInfo.albumArtist))
        self.setItem(self.nrows, 5, QTableWidgetItem(str(mediaInfo.year) if mediaInfo.year != -1 else ""))
        self.setItem(self.nrows, 6, QTableWidgetItem("")) # filler
        self.setRowHeight(self.nrows, 40)
        self.nrows += 1

    def mediasAdded(self, medias, append=True, highlight=None):
        if append:
          self.mediaRow += medias
        medias = iter(medias)
        self.mediaBatch += 1
        batchNo = self.mediaBatch
        def iteration():
            if self.mediaBatch != batchNo:
                return
            try:
                self.addMedia(next(medias), highlight)
                QTimer.singleShot(1, iteration)
            except:
                return
        # wait for the previous set of iteration
        # to finish before firing another one
        QTimer.singleShot(2, iteration)

    # data manip
    def sortAndFilter(self):
        if self.filterText:
            self.specialFilter = True
            matches = FILTER_REGEX.findall(self.filterText)
            print(matches)
            if matches:
                matches = list(map(lambda m: (m[0], m[1].lower()), matches))
                def func(media):
                    for (key, value) in matches:
                        if key == "artist":
                            if value not in media.artist.lower():
                                return False
                        elif key == "album":
                            if value not in media.album.lower():
                                return False
                        elif key == "aartist":
                            if value not in media.albumArtist.lower():
                                return False
                    return True
                self.mediaRow = list(filter(func, Application.mainWindow.medias))
            else:
                self.specialFilter = False
                self.mediaRow = list(filter(lambda media: self.filterText.lower() in media.title.lower(), Application.mainWindow.medias))
        else:
            self.mediaRow = Application.mainWindow.medias

        self.clearContents()
        self.nrows = 0
        self.setRowCount(0)
        if not self.mediaRow:
            self.mediaBatch += 1
            QTimer.singleShot(2, lambda: self.clearContents())
            return

        self.mediaRow.sort(key=attrgetter(self.sortKey), reverse=self.sortRev)
        self.mediasAdded(self.mediaRow, False, self.filterText)

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

        self.sortAndFilter()

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
        if self.hoverRow == -1: return
        if  e.modifiers() & Qt.ControlModifier or \
            e.modifiers() & Qt.ShiftModifier:
            return
        index = self.indexAt(e.pos())
        mainWindow = Application.mainWindow
        if self.mediaRow:
            if mainWindow.mediaInfo and self.mediaRow[index.row()] == mainWindow.mediaInfo:
                return
            mainWindow.setSong(self.mediaRow[index.row()])


class FileListView(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.initUI()
        self.bindEvents()
        self.mpos = None

    def initUI(self):
        vboxLayout = QVBoxLayout()
        vboxLayout.setContentsMargins(0,0,0,0)
        vboxLayout.setSpacing(0)
        self.setLayout(vboxLayout)

        self.searchView = SearchView()
        self.searchView.hide()
        vboxLayout.addWidget(self.searchView)

        self.tableWidget = tableWidget = FileListTableWidget()
        tableWidget.resizeEvent = self.tableResizeEvent
        tableWidget.setAlternatingRowColors(True)
        vboxLayout.addWidget(tableWidget, 1)

        self.scrollBar = tableWidget.verticalScrollBar()
        self.scrollBar.setParent(self)
        self.scrollBar.show()

        if Application.mainWindow.medias:
            self.tableWidget.mediasAdded(Application.mainWindow.medias)
            self.tableWidget.selectPlaying()

    # events
    def bindEvents(self):
        Application.mainWindow.mediasAdded.connect(self.tableWidget.mediasAdded)
        Application.mainWindow.mediasUpdated.connect(self.tableWidget.sortAndFilter)
        Application.mainWindow.songInfoChanged.connect(self.tableWidget.selectPlaying)

    def tableResizeEvent(self, event):
        QTableWidget.resizeEvent(self.tableWidget, event)
        WIDTH = self.scrollBar.sizeHint().width()
        self.scrollBar.setGeometry(QRect(
            self.tableWidget.width()-WIDTH,
            self.tableWidget.y()+self.tableWidget.horizontalHeader().height(),
            WIDTH, self.tableWidget.height()-self.tableWidget.horizontalHeader().height()
        ))
