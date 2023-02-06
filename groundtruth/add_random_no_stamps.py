import csv
import random
from pathlib import Path

NO_STAMPS = []

def add_imgs(i, imgs_with_stamps = []):
    global NO_STAMPS
    wlname = "W"+i[1:-4]
    fname = "../imageinfos/"+wlname+"-"+i+".csv"
    if not Path(fname).is_file():
        #print("ignoring "+fname)
        return
    with open(fname, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        next(reader)
        for row in reader:
            if row[0] not in imgs_with_stamps:
                NO_STAMPS.append(row[0])

def read_iinfos():
    with open("../nlm-volumeinfos.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            if row[3] == "1":
                add_imgs(row[2])

def read_rkts():
    itoimgs = {}
    with open("stamp_number_rkts.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            i = row[0][:row[0].find("_")+4]
            if i not in itoimgs:
                itoimgs[i] = []
            itoimgs[i].append(row[0])
    for i, ilist in itoimgs.items():
        add_imgs(i, ilist)

read_iinfos()
read_rkts()

random_sample = random.sample(NO_STAMPS, 4000)
for img in random_sample:
    print(img)