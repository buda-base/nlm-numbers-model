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

def all_text_changes():
    res = {}
    with open("results/all_text_changes.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            res[row[0]] = True
    return res

TC = all_text_changes()

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

def analyze_volume(batchdir, jsonlfn, stats, sort_for_false_positives, sort_for_false_negatives, sort_for_false_negatives_pos, not_very_high, grand_outline):
    basefn = jsonlfn[len(batchdir):-6]
    [wlname, ilname] = basefn.split("-")
    #if wlname != "W1NLM2371":
    #    return
    if ilname not in VINFO:
        #print(ilname)
        return
    vinfo = VINFO[ilname]
    images = get_images(jsonlfn)
    nvh = set()
    for imgnum, image in enumerate(images):
        if float(image[2]) >= 0.2:
            continue
        if image[0] in TC:
            nvh.add(image[0])
    from_training = []
    if wlname+"-"+ilname in TRAINING_DATA["with"]:
        from_training = TRAINING_DATA["with"][wlname+"-"+ilname]
        nvh.difference_update(from_training)
    if wlname+"-"+ilname in TRAINING_DATA["without"]:
        from_training = TRAINING_DATA["without"][wlname+"-"+ilname]
        nvh.difference_update(from_training)
    not_very_high += list(nvh)

def download_images(imagelist, folder):
    for imgfname in tqdm(sorted(imagelist)):
        if Path(folder+imgfname).is_file():
            continue
        wlname = "W"+imgfname[1:imgfname.find("_")]
        ilname = imgfname[:imgfname.find("_")+4]
        try:
            img = get_processed_image(wlname, ilname, imgfname)
            img.save(folder+imgfname, "JPEG", progressive=True, optimize=True)
        except Exception as e:
            print("couldn't download "+imgfname)
            print(e)

def main(batchdir, analysisdir):
    jsonlfns = sorted(glob(batchdir+"*.jsonl"))
    sort_for_false_negatives = []
    sort_for_false_positives = []
    sort_for_false_negatives_pos = []
    not_very_high = []
    grand_outline = []
    stats = {
        "missing_numbers": 0,
        "missing_numbers_vol": 0,
        "additional_numbers": 0,
        "additional_numbers_vol": 0,
        "correct_numbers": 0,
        "correct_numbers_vol": 0
    }
    for jsonlfn in jsonlfns:
        analyze_volume(batchdir, jsonlfn, stats, sort_for_false_positives, sort_for_false_negatives, sort_for_false_negatives_pos, not_very_high, grand_outline)
    print(stats)
    #download_images(sort_for_false_positives, analysisdir+"positives/")
    #download_images(sort_for_false_negatives_pos, analysisdir+"negative-pos/")
    #download_images(sort_for_false_negatives, analysisdir+"negatives/")
    download_images(not_very_high, analysisdir+"nvh/")

main("results/batch2/", "analyses/batch4/")