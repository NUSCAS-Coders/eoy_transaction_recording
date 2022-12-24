from commons.Singleton import Singleton


class GlobalState(metaclass = Singleton):
    artists = {}
    artistNameDict = {}
    artistIdDict = {}
