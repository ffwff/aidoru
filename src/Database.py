import os
import pickle

class Database:

    BASE = os.path.expanduser("~/.aidoru")
    EXT = ".pkl"

    def save(obj, filename):
        os.makedirs(Database.BASE, exist_ok=True)
        with open(os.path.join(Database.BASE, filename + Database.EXT), "wb") as f:
            pickle.dump(obj, f)

    def load(filename):
        try:
            with open(os.path.join(Database.BASE, filename + Database.EXT), "rb") as f:
                return pickle.load(f)
        except:
            return None
