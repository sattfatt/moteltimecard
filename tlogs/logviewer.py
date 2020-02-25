import pickle
import sys

def load_dict(path):
    dictionary = pickle.load(open(path, "rb"))
    return dictionary

def print_dict(dictionary):
    for key, val in dictionary.items():
        print(key)
        for tup in val:
            print(tup[0].strftime("%H:%M:%S") + " " + tup[1])

PATH = sys.argv[1]
if(PATH):
    dictionary = load_dict(PATH)
    print_dict(dictionary)
else:
    print("Did not specify a file!")
