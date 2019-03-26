import dbus
import dbus.service
import dbus.mainloop.glib
from src.Application import Application
from src.modules.module import BaseModule

class MprisService(dbus.service.Object):

    def __init__(self, mainWindow):
        bus = dbus.service.BusName(
            "org.mpris.MediaPlayer2.aidoru",
            bus=dbus.SessionBus())
        super().__init__(bus, "/org/mpris/MediaPlayer2")

        self._properties = dbus.Dictionary({
            'DesktopEntry': 'aidoru',
            'Identity': 'aidoru'
        }, signature='sv')
        self._player_properties = dbus.Dictionary({
            "Metadata": dbus.Dictionary({
                'mpris:trackId': '/0',
                'mpris:artUrl': '',
                'xesam:artist': ['None'],
                'xesam:title': 'None',
                'xesam:album': 'None'
            }, signature='sv', variant_level=1),
            'CanGoNext': True,
            'CanGoPrevious': True,
            'CanPause': True,
            'CanPlay': True,
            'CanControl': True,
            'CanStop': True,
        }, signature='sv', variant_level=2)

        self.mainWindow = mainWindow
        self.mainWindow.songInfoChanged.connect(self.songInfoChanged)

    # events
    def songInfoChanged(self, mediaInfo):
        if mediaInfo.albumArtist == mediaInfo.artist:
            artist = [mediaInfo.artist]
        else:
            artist = [mediaInfo.artist, mediaInfo.albumArtist]
        props = dbus.Dictionary({
            'Metadata': dbus.Dictionary({
                'mpris:trackId': '/0',
                'mpris:artUrl': mediaInfo.image,
                'xesam:artist': artist,
                'xesam:title': mediaInfo.title,
                'xesam:album': mediaInfo.album
            }, signature='sv')
        }, signature='sv')
        self._player_properties.update(props)
        self.PropertiesChanged('org.mpris.MediaPlayer2.Player', props, [])

    # methods
    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Previous(self):
        self.mainWindow.prevSong()

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Next(self):
        self.mainWindow.nextSong()

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Play(self):
        self.mainWindow.media.play()

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Pause(self):
        self.mainWindow.media.pause()

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def PlayPause(self):
        self.mainWindow.playPause()

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Seek(self, offset):
        pass

    # properties
    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
        return self.GetAll(interface)[prop]

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        print(interface)
        if interface == "org.mpris.MediaPlayer2":
            return self._properties
        elif interface == "org.mpris.MediaPlayer2.Player":
            return self._player_properties

class MprisModule(BaseModule):

    def __init__(self):
        BaseModule.__init__(self, "MPRIS integration for Linux")
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    def enable(self):
        BaseModule.enable(self)
        self.service = MprisService(Application.mainWindow)

    def disable(self):
        return
