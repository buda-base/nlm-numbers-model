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
            res[row[2]] = {"nb_texts": int(row[3]), "numbers": row[7].split(", ")}
    return res

VINFO = get_volinfos()

STRIKEDTHROUGH = [
    'I1NLM3081_0010104.jpg', 
    'I1NLM3486_0010199.jpg', 
    'I1NLM3852_0010276.jpg', 
    'I1NLM3870_0010013.jpg', 
    'I1NLM3870_0010037.jpg', 
    'I1NLM4202_0010064.jpg', 
    'I1NLM4191_0010116.jpg', 
    'I1NLM4246_0010209.jpg',
    'I1NLM4446_0010220.jpg',
    'I1NLM5003_0010173.jpg',
    'I1NLM4316_0010040.jpg', 
    'I1NLM4669_0010324.jpg', 
    'I1NLM5148_0010293.jpg', 
    'I1NLM5329_0010257.jpg', 
    'I1NLM5414_0010157.jpg', 
    'I1NLM3478_0010169.jpg', 
    'I1NLM3486_0010199.jpg', 
    'I1NLM3645_0010259.jpg', 
    'I1NLM3852_0010276.jpg',
    'I1NLM2131_0010193.jpg',
    'I1NLM4992_0010190.jpg',
    'I1NLM970_0010156.jpg',
    'I1NLM3510_0010228.jpg',
    'I1NLM1634_0010257.jpg',
    'I1NLM1682_0010076.jpg',
    'I1NLM4684_0010279.jpg',
    'I1NLM4637_0010187.jpg',
    'I1NLM5336_0010253.jpg',
    'I1NLM2801_0010169.jpg',
    'I1NLM1713_0010200.jpg',
    'I1NLM4202_0010276.jpg',
    'I1NLM43_0010231.jpg',
    'I1NLM50_0010125.jpg',
    'I1NLM4773_0010045.jpg',
    'I1NLM1708_0010281.jpg',
    'I1NLM3592_0010134.jpg',
    'I1NLM1140_0010258.jpg',
    'I1NLM5304_0010244.jpg',
    'I1NLM2169_0010058.jpg',
    'I1NLM4626_0010207.jpg',
    'I1NLM270_0010021.jpg',
    'I1NLM4881_0010099.jpg',
    'I1NLM5450_0010071.jpg',
    'I1NLM3641_0010270.jpg',
    'I1NLM1777_0010124.jpg',
    'I1NLM4415_0010217.jpg',
    'I1NLM22_0010119.jpg',
    'I1NLM4202_0010064.jpg',
    'I1NLM1009_0010075.jpg',
    'I1NLM349_0010024.jpg',
    'I1NLM2038_0010267.jpg',
    'I1NLM4373_0010084.jpg',
    'I1NLM2014_0010112.jpg'
]

DUPLICATES = [
    'I1NLM113_0010148.jpg',
    'I1NLM2261_0010195.jpg',
    'I1NLM4416_0010170.jpg',
    'I1NLM2656_0010083.jpg',
    'I1NLM1158_0010219.jpg',
    'I1NLM48_0010376.jpg',
    'I1NLM1646_0010249.jpg',
    'I1NLM4182_0010193.jpg',
    'I1NLM1484_0010065.jpg',
    'I1NLM1683_0010193.jpg',
    'I1NLM1960_0010220.jpg',
    'I1NLM4747_0010189.jpg',
    'I1NLM4785_0010318.jpg',
    'I1NLM3891_0010204.jpg',
    'I1NLM212_0010123.jpg',
    'I1NLM3480_0010069.jpg',
    'I1NLM1625_0010055.jpg',
    'I1NLM1674_0010171.jpg',
    'I1NLM4776_0010098.jpg',
    'I1NLM1484_0010117.jpg',
    'I1NLM3481_0010178.jpg',
    'I1NLM730_0010115.jpg',
    'I1NLM5171_0010130.jpg',
    'I1NLM186_0010208.jpg',
    'I1NLM2682_0010176.jpg',
    'I1NLM4212_0010113.jpg'
]

IGNORE = ['I1NLM1511_0010199']

DOUBLE = [
    'I1NLM3870_0010041.jpg',
    'I1NLM2801_0010239.jpg',
    'I1NLM2801_0010330.jpg',
    'I1NLM3990_0010124.jpg',
    'I1NLM4033_0010278.jpg',
    'I1NLM4033_0010293.jpg',
    'I1NLM4033_0010294.jpg',
    'I1NLM5512_0010024.jpg',
    'I1NLM4033_0010295.jpg',
    'I1NLM4033_0010296.jpg'
]

NO_STAMP_TEXT_BREAK = [
    'I1NLM5561_0010135.jpg',
    'I1NLM1581_0010230.jpg',
    'I1NLM5009_0010029.jpg',
    'I1NLM4077_0010239.jpg'
]

TRIPLE = [
    'I1NLM4033_0010297.jpg',
    'I1NLM3990_0010126.jpg'
]

QUAD = [
    'I1NLM5190_0010400.jpg'
]

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
P_LIMIT_SECOND = 0.01

def get_images(jsonlfn):
    res = []
    with open(jsonlfn, 'r') as json_file:
        for l in json_file:
            res.append(json.loads(l))
    return res

def analyze_volume(batchdir, jsonlfn, stats, sort_for_false_positives, sort_for_false_negatives, sort_for_false_negatives_pos, not_very_high):
    basefn = jsonlfn[len(batchdir):-6]
    [wlname, ilname] = basefn.split("-")
    #if wlname != "W1NLM26":
    #    return
    vinfo = VINFO[ilname]
    nb_numbers_expected = vinfo["nb_texts"]
    images = get_images(jsonlfn)
    nb_detected = 0
    # sort from higher to lower
    images = sorted(images, key=lambda x: x[1])
    positives = set()
    less_positives = set()
    nvh = set()
    nb_strikedthrough = 0
    nb_double = 0
    nb_triple = 0
    for imgnum, image in enumerate(images):
        has_number = float(image[2]) >= P_LIMIT
        if has_number:
            positives.add(image[0])
            if float(image[2]) <= 0.9:
                nvh.add(image[0])
        elif float(image[2]) > 0:
            less_positives.add(image[0])
    from_training = []
    needsfirst = False
    if wlname+"-"+ilname in TRAINING_DATA["with"]:
        from_training = TRAINING_DATA["with"][wlname+"-"+ilname]
        positives.update(from_training)
        less_positives.difference_update(from_training)
        nvh.difference_update(from_training)
        needsfirst = True
        for img in from_training:
            if img.endswith("0001.jpg") or img.endswith("0002.jpg") or img.endswith("0003.jpg"):
                needsfirst = False
                break
    else:
        needsfirst = True
    for img in positives:
        if img in STRIKEDTHROUGH or img in DUPLICATES or img in IGNORE:
            nb_strikedthrough += 1
        if img in DOUBLE:
            nb_double += 1
        if img in TRIPLE:
            nb_triple += 1
    #print(sorted(list(positives)))
    if wlname+"-"+ilname in TRAINING_DATA["without"]:
        from_training = TRAINING_DATA["without"][wlname+"-"+ilname]
        #print("discard "+str(len(from_training)))
        for img in from_training:
            positives.discard(img)
            less_positives.discard(img)
            nvh.discard(img)
    if needsfirst:
        positives.add(ilname+"0001.jpg")
    not_very_high+=list(nvh)
    positives = sorted(list(positives))
    nb_detected = len(positives) - nb_strikedthrough + nb_double + 2 * nb_triple
    if nb_detected > nb_numbers_expected:
        stats["additional_numbers"] += nb_detected - nb_numbers_expected
        stats["additional_numbers_vol"] += 1
        stats["correct_numbers"] += nb_numbers_expected
        sort_for_false_positives += list(positives)
        # if we detected N too many numbers, we look at the N detected with
        # the lowest probability
        #for i in range(nb_numbers_expected, nb_detected):
        #    sort_for_false_positives + list(positives)
    elif nb_detected < nb_numbers_expected:
        stats["missing_numbers"] += nb_numbers_expected - nb_detected
        stats["missing_numbers_vol"] += 1
        stats["correct_numbers"] += nb_detected
        sort_for_false_negatives_pos += list(positives)[1:]
        create_outline(wlname, ilname, positives)
        #for i in range(nb_detected, nb_numbers_expected):
        #    sort_for_false_negatives.append(images[i][0])
        # different aproach: we take everything between 0.2 and 0.5
        sort_for_false_negatives += list(less_positives)
    else:
        stats["correct_numbers"] += nb_detected
        stats["correct_numbers_vol"] += 1

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

def create_outline(wlname,ilname,positives):
    rows = []
    numbers = VINFO[ilname]["numbers"]
    spos = sorted(list(positives))
    nbrows = max(len(numbers), len(spos))
    for i in range(nbrows):
        num = numbers[i] if i < len(numbers) else ""
        img_cell = ""
        img="?"
        full_link=""
        if i < len(spos):
            img = spos[i]
            img_cell = '=IMAGE("https://iiif.bdrc.io/bdr:'+ilname+'::'+img+'/0,0,500,1000/pct:50/270/default.jpg")'
            full_link = "https://iiif.bdrc.io/bdr:"+ilname+"::"+img+"/full/max/0/default.jpg"
        rows.append([full_link,img,num])
    csvfname = "analyses/batch2/outlines/"+wlname+".csv"
    with open(csvfname, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        for r in rows:
            writer.writerow(r)


def main(batchdir, analysisdir):
    jsonlfns = sorted(glob(batchdir+"*.jsonl"))
    sort_for_false_negatives = []
    sort_for_false_positives = []
    sort_for_false_negatives_pos = []
    not_very_high = []
    stats = {
        "missing_numbers": 0,
        "missing_numbers_vol": 0,
        "additional_numbers": 0,
        "additional_numbers_vol": 0,
        "correct_numbers": 0,
        "correct_numbers_vol": 0
    }
    for jsonlfn in jsonlfns:
        analyze_volume(batchdir, jsonlfn, stats, sort_for_false_positives, sort_for_false_negatives, sort_for_false_negatives_pos, not_very_high)
    print(stats)
    #download_images(sort_for_false_positives, analysisdir+"positives/")
    #download_images(sort_for_false_negatives_pos, analysisdir+"negative-pos/")
    #download_images(sort_for_false_negatives, analysisdir+"negatives/")
    download_images(not_very_high, analysisdir+"nvh/")

main("results/batch2/", "analyses/batch2/")