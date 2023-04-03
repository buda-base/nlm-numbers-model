import csv
from glob import glob
import json
from tqdm import tqdm
from create_images import get_processed_image
from pathlib import Path
import random

def get_volinfos():
    res = {}
    with open("nlm-volumeinfos.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        #for i in range(5390):
        #    next(reader)
        for row in reader:
            res[row[2]] = {"nb_texts": int(row[3]), "numbers": row[7].split(", ")}
            #print(row[2])
    return res

VINFO = get_volinfos()

def get_images(jsonlfn):
    res = []
    with open(jsonlfn, 'r') as json_file:
        for l in json_file:
            res.append(json.loads(l))
    return res

TRAINING_DATA = {}
def get_training_data(name, category):
    global TRAINING_DATA
    if category not in TRAINING_DATA:
        TRAINING_DATA[category] = {}
    csv_fname = "groundtruth/"+name+".csv"
    with open(csv_fname, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            imgfname = row[0]
            basename = imgfname[1:imgfname.find("_")]
            wlname = "W"+basename
            ilname = "I"+basename+"_001"
            if wlname+"-"+ilname not in TRAINING_DATA[category]:
                TRAINING_DATA[category][wlname+"-"+ilname] = []
            TRAINING_DATA[category][wlname+"-"+ilname].append(imgfname)

get_training_data("difficult", "with")
get_training_data("stamp_number", "with")
get_training_data("no_stamp", "without")

def analyze_volume(batchdir, jsonlfn, stats):
    basefn = jsonlfn[len(batchdir):-6]
    [wlname, ilname] = basefn.split("-")
    #if wlname != "W1NLM2371":
    #    return
    if ilname not in VINFO:
        #print(ilname)
        return
    vinfo = VINFO[ilname]
    images = get_images(jsonlfn)
    from_training_negatives = []
    from_training_positives = []
    if wlname+"-"+ilname in TRAINING_DATA["with"]:
        from_training_positives = TRAINING_DATA["with"][wlname+"-"+ilname]
    if wlname+"-"+ilname in TRAINING_DATA["without"]:
        from_training_negatives = TRAINING_DATA["without"][wlname+"-"+ilname]
    for imgnum, image in enumerate(images):
        t = "true_positives"
        p = float(image[2])
        if p < 0.2:
            t = "true_negatives"
            if image[0] in from_training_positives:
                t = "false_negatives"
            stats[t].append(image[0])
        elif p > 0.8:
            t = "true_positives"
            if image[0] in from_training_negatives:
                t = "false_positives"
            stats[t].append(image[0])
        if p < 0.65 and p > 0.35:
            stats["ambiguous"].append(image[0])

SAMPLE_SIZE = 1000

def get_sample(l):
    if len(l) <= SAMPLE_SIZE:
        return l
    return random.sample(l, SAMPLE_SIZE)

def main(batchdir):
    jsonlfns = sorted(glob(batchdir+"*.jsonl"))
    stats = {
        "true_positives": [],
        "false_positives": [],
        "true_negatives": [],
        "false_negatives": [],
        "ambiguous": []
    }
    for jsonlfn in jsonlfns:
        analyze_volume(batchdir, jsonlfn, stats)
    for img in get_sample(stats["true_positives"]):
        print("tp,"+img)
    for img in get_sample(stats["false_positives"]):
        print("fp,"+img)
    for img in get_sample(stats["true_negatives"]):
        print("tn,"+img)
    for img in get_sample(stats["false_negatives"]):
        print("fn,"+img)
    for img in get_sample(stats["ambiguous"]):
        print("a,"+img)

main("results/batch2/")