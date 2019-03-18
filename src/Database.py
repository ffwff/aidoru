import os
import pickle
import json
from shutil import copyfile

class Database:

    BASE = os.path.expanduser("~/.aidoru")

    def getPath(filename):
        return os.path.join(Database.BASE, filename)

    def save(obj, filename, save_json=False):
        os.makedirs(Database.BASE, exist_ok=True)
        with open(Database.getPath(filename), ("w" if save_json else "wb")) as f:
            (json if save_json else pickle).dump(obj, f)

    def load(filename, load_json=False, default={}):
        try:
            with open(Database.getPath(filename), ("r" if load_json else "rb")) as f:
                obj = (json if load_json else pickle).load(f)
                return {**default, **obj}
        except FileNotFoundError:
            print("can't load %s" % filename)
            return default

    def loadFile(filename, default=""):
        try:
            with open(Database.getPath(filename), "r") as f:
                return f.read()
        except:
            if not default: return ""
            dfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), default)
            with open(dfile, "r") as f:
                return f.read()
