import csv
from glob import glob
import json

def get_volinfos():
    res = {}
    with open("nlm-volumeinfos.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            res[row[2]] = {"nb_texts": int(row[3])}
    return res

VINFO = get_volinfos()

P_LIMIT = 0.8

def get_images(jsonlfn):
    res = []
    with open(jsonlfn, 'r') as json_file:
        for l in json_file:
            res.append(json.loads(l))
    return res

def analyze_volume(batchdir, jsonlfn, stats):
    basefn = jsonlfn[len(batchdir):-6]
    [wlname, ilname] = basefn.split("-")
    vinfo = VINFO[ilname]
    nb_numbers_expected = vinfo["nb_texts"]
    images = get_images(jsonlfn)
    previous_has_number = False
    nb_images = len(images)
    nb_detected = 0
    for imgnum, image in enumerate(images):
        has_number = float(image[2]) >= P_LIMIT
        if has_number:
            if previous_has_number:
                # when there are numbers inferred on two consecutive images we ignore the second one
                stats["additional_numbers_fixable"] += 1
            elif imgnum >= nb_images -2:
                # we ignore numbers detected on the final 2 images which we assume are covers
                stats["additional_numbers_fixable"] += 1
            else:
                nb_detected += 1
            previous_has_number = True
        else:
            previous_has_number = False
    if nb_detected > nb_numbers_expected:
        stats["additional_numbers"] += nb_detected - nb_numbers_expected
        stats["correct_numbers"] += nb_numbers_expected
    elif nb_detected < nb_numbers_expected:
        stats["missing_numbers"] += nb_numbers_expected - nb_detected
        stats["correct_numbers"] += nb_detected
    else:
        stats["correct_numbers"] += nb_detected

def main(batchdir):
    jsonlfns = sorted(glob(batchdir+"*.jsonl"))
    stats = {
        "missing_numbers": 0,
        "additional_numbers": 0,
        "additional_numbers_fixable": 0,
        "correct_numbers": 0,
    }
    for jsonlfn in jsonlfns:
        analyze_volume(batchdir, jsonlfn, stats)
    print(stats)

main("results/batch1/")