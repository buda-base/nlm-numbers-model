import csv
from glob import glob
import json
from tqdm import tqdm
from create_images import get_processed_image
from pathlib import Path

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
        if float(image[2]) < 0.5:
            t = "true_negatives"
            if image[0] in from_training_positives:
                t = "false_negatives"
        elif image[0] in from_training_negatives:
            t = "false_positives"
        stats[t] += 1
    

def main(batchdir, analysisdir):
    jsonlfns = sorted(glob(batchdir+"*.jsonl"))
    stats = {
        "true_positives": 0,
        "false_positives": 0,
        "true_negatives": 0,
        "false_negatives": 0,
    }
    for jsonlfn in jsonlfns:
        analyze_volume(batchdir, jsonlfn, stats)
    print(stats)
    precision = stats["true_positives"] / (stats["true_positives"] + stats["false_positives"])
    recall = stats["true_positives"] / (stats["true_positives"] + stats["false_negatives"])
    f = (2 * precision * recall) / (precision + recall)
    print("precision = %f, recall = %f, f = %f" % (precision, recall, f))

main("results/batch2/", "analyses/batch4/")