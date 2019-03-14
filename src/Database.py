import os
import pickle
from shutil import copyfile

class Database:

    BASE = os.path.expanduser("~/.aidoru")
    EXT = ".pkl"

    def getPath(filename):
        return os.path.join(Database.BASE, filename)

    def save(obj, filename):
        os.makedirs(Database.BASE, exist_ok=True)
        with open(Database.getPath(filename) + Database.EXT, "wb") as f:
            pickle.dump(obj, f)

    def load(filename):
        try:
            with open(Database.getPath(filename) + Database.EXT, "rb") as f:
                return pickle.load(f)
        except:
            return None

    def loadFile(filename, default=""):
        try:
            with open(Database.getPath(filename), "r") as f:
                return f.read()
        except:
            if not default: return ""
            dfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), default)
            with open(dfile, "r") as f:
                return f.read()
