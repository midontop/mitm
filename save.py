import os
import pickle

for f in os.listdir("weekly"):
    if f.endswith(".py") and not f.startswith("__init__"):
        # every file contains a variable called weekly. Pickle the file and save it to pickles.
        with open(os.path.join("pickles", f[:-3]+".pickle"), "wb") as fp:
            # import the file and pickle the variable 
            m = __import__("weekly." + f[:-3])
            pickle.dump(m.weekly, fp)