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
        for row in reader:
            res[row[2]] = {"nb_texts": int(row[3])}
    return res

VINFO = get_volinfos()


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
get_training_data("stamp_number_rkts", "with")
get_training_data("no_stamp", "without")

#print(TRAINING_DATA)

P_LIMIT = 0.5

def get_images(jsonlfn):
    res = []
    with open(jsonlfn, 'r') as json_file:
        for l in json_file:
            res.append(json.loads(l))
    return res

def analyze_volume(batchdir, jsonlfn, stats, sort_for_false_positives, sort_for_false_negatives):
    basefn = jsonlfn[len(batchdir):-6]
    [wlname, ilname] = basefn.split("-")
    vinfo = VINFO[ilname]
    nb_numbers_expected = vinfo["nb_texts"]
    images = get_images(jsonlfn)
    nb_detected = 0
    # sort from higher to lower
    images = sorted(images, key=lambda x: x[1])
    positives = set()
    for imgnum, image in enumerate(images):
        has_number = float(image[2]) >= P_LIMIT
        if has_number:
            positives.add(image[0])
    from_training = []
    if wlname+"-"+ilname in TRAINING_DATA["with"]:
        from_training = TRAINING_DATA["with"][wlname+"-"+ilname]
        positives.update(from_training)
    positives = sorted(list(positives))
    nb_detected = len(positives)
    if nb_detected > nb_numbers_expected:
        stats["additional_numbers"] += nb_detected - nb_numbers_expected
        stats["additional_numbers_vol"] += 1
        stats["correct_numbers"] += nb_numbers_expected
        # if we detected N too many numbers, we look at the N detected with
        # the lowest probability
        for i in range(nb_numbers_expected, nb_detected):
            sort_for_false_positives.append(images[i][0])
    elif nb_detected < nb_numbers_expected:
        stats["missing_numbers"] += nb_numbers_expected - nb_detected
        stats["missing_numbers_vol"] += 1
        stats["correct_numbers"] += nb_detected
        #for i in range(nb_detected, nb_numbers_expected):
        #    sort_for_false_negatives.append(images[i][0])
    else:
        stats["correct_numbers"] += nb_detected
        stats["correct_numbers_vol"] += 1

def download_images(imagelist, folder):
    for imgfname in tqdm(imagelist):
        if Path(folder+imgfname).is_file():
            continue
        wlname = "W"+imgfname[1:imgfname.find("_")]
        ilname = imgfname[:imgfname.find("_")+4]
        img = get_processed_image(wlname, ilname, imgfname)
        img.save(folder+imgfname, "JPEG", progressive=True, optimize=True)

def main(batchdir, analysisdir):
    jsonlfns = sorted(glob(batchdir+"*.jsonl"))
    sort_for_false_negatives = []
    sort_for_false_positives = []
    stats = {
        "missing_numbers": 0,
        "missing_numbers_vol": 0,
        "additional_numbers": 0,
        "additional_numbers_vol": 0,
        "correct_numbers": 0,
        "correct_numbers_vol": 0
    }
    for jsonlfn in jsonlfns:
        analyze_volume(batchdir, jsonlfn, stats, sort_for_false_positives, sort_for_false_negatives)
    print(stats)
    download_images(sort_for_false_positives, analysisdir+"positives/")
    #download_images(sort_for_false_negatives, analysisdir+"negatives/")

main("results/batch2/", "analyses/batch2/")