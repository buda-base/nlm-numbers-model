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

def get_irreg_before():
    res = []
    with open("analyses/batch2/negative-pos-diff.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            res.append(row[0])
    return res

IRREGULARITY_BEFORE = get_irreg_before()

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
    'I1NLM2014_0010112.jpg',
    'I1NLM4304_0010299.jpg',
    'I1NLM4446_0010220.jpg',
    'I1NLM4934_0010336.jpg',
    'I1NLM5003_0010173.jpg'
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
    'I1NLM4212_0010113.jpg',
    'I1NLM1484_0010117.jpg',
    'I1NLM1804_0010185.jpg'
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
    'I1NLM4033_0010296.jpg',
    'I1NLM137_0010112.jpg',
    'I1NLM150_0010192.jpg',
    'I1NLM150_0010193.jpg'
    'I1NLM236_0010112.jpg',
    'I1NLM252_0010024.jpg',
    'I1NLM257_0010030.jpg',
    'I1NLM259_0010012.jpg',
    'I1NLM259_0010045.jpg',
    'I1NLM260_0010013.jpg',
    'I1NLM260_0010047.jpg',
    'I1NLM280_0010077.jpg',
    'I1NLM365_0010326.jpg',
    'I1NLM418_0010064.jpg',
    'I1NLM418_0010187.jpg',
    'I1NLM446_0010147.jpg',
    'I1NLM446_0010159.jpg',
    'I1NLM481_0010058.jpg',
    'I1NLM481_0010060.jpg',
    'I1NLM481_0010062.jpg',
    'I1NLM481_0010065.jpg',
    'I1NLM481_0010069.jpg',
    'I1NLM554_0010013.jpg',
    'I1NLM554_0010067.jpg',
    'I1NLM572_0010019.jpg',
    'I1NLM572_0010044.jpg',
    'I1NLM592_0010144.jpg',
    'I1NLM602_0010203.jpg',
    'I1NLM616_0010049.jpg',
    'I1NLM638_0010184.jpg',
    'I1NLM653_0010094.jpg',
    'I1NLM655_0010204.jpg',
    'I1NLM655_0010209.jpg',
    'I1NLM655_0010219.jpg',
    'I1NLM680_0010033.jpg',
    'I1NLM680_0010035.jpg',
    'I1NLM746_0010079.jpg',
    'I1NLM783_0010005.jpg',
    'I1NLM783_0010101.jpg',
    'I1NLM819_0010022.jpg',
    'I1NLM884_0010022.jpg',
    'I1NLM884_0010058.jpg',
    'I1NLM884_0010078.jpg',
    'I1NLM1065_0010023.jpg',
    'I1NLM1114_0010312.jpg',
    'I1NLM1227_0010319.jpg',
    'I1NLM1296_0010429.jpg',
    'I1NLM1296_0010443.jpg',
    'I1NLM1296_0010577.jpg',
    'I1NLM1316_0010196.jpg',
    'I1NLM1342_0010157.jpg',
    'I1NLM1344_0010341.jpg',
    'I1NLM1349_0010126.jpg',
    'I1NLM1349_0010136.jpg',
    'I1NLM1349_0010144.jpg',
    'I1NLM1352_0010100.jpg',
    'I1NLM1380_0010219.jpg',
    'I1NLM1479_0010397.jpg',
    'I1NLM1491_0010173.jpg',
    'I1NLM1722_0010226.jpg',
    'I1NLM1804_0010090.jpg',
    'I1NLM1816_0010301.jpg',
    'I1NLM1975_0010082.jpg',
    'I1NLM1975_0010084.jpg',
    'I1NLM2039_0010133.jpg',
    'I1NLM2043_0010120.jpg',
    'I1NLM2124_0010174.jpg',
    'I1NLM2135_0010116.jpg',
    'I1NLM2160_0010053.jpg',
    'I1NLM2160_0010064.jpg',
    'I1NLM2175_0010186.jpg',
    'I1NLM2203_0010141.jpg',
    'I1NLM2212_0010082.jpg',
    'I1NLM2220_0010135.jpg',
    'I1NLM2224_0010195.jpg',
    'I1NLM2244_0010171.jpg',
    'I1NLM2302_0010105.jpg',
    'I1NLM2618_0010010.jpg',
    'I1NLM2618_0010021.jpg',
    'I1NLM2802_0010211.jpg',
    'I1NLM2805_0010186.jpg',
    'I1NLM2807_0010089.jpg',
    'I1NLM2941_0010180.jpg',
    'I1NLM2941_0010276.jpg',
    'I1NLM3041_0010193.jpg',
    'I1NLM3073_0010110.jpg',
    'I1NLM3078_0010140.jpg',
    'I1NLM3100_0010110.jpg',
    'I1NLM3139_0010133.jpg',
    'I1NLM3242_0010159.jpg',
    'I1NLM3286_0010156.jpg',
    'I1NLM3286_0010157.jpg',
    'I1NLM3297_0010422.jpg',
    'I1NLM3507_0010081.jpg',
    'I1NLM3511_0010112.jpg',
    'I1NLM3696_0010079.jpg',
    'I1NLM3696_0010135.jpg',
    'I1NLM3696_0010176.jpg',
    'I1NLM3842_0010219.jpg',
    'I1NLM3856_0010167.jpg',
    'I1NLM3990_0010102.jpg',
    'I1NLM3990_0010105.jpg',
    'I1NLM3990_0010124.jpg',
    'I1NLM3990_0010133.jpg',
    'I1NLM4011_0010161.jpg',
    'I1NLM4193_0010291.jpg',
    'I1NLM4194_0010267.jpg',
    'I1NLM4266_0010083.jpg',
    'I1NLM4288_0010169.jpg',
    'I1NLM4381_0010206.jpg',
    'I1NLM4414_0010460.jpg',
    'I1NLM4446_0010234.jpg',
    'I1NLM4446_0010254.jpg',
    'I1NLM4523_0010067.jpg',
    'I1NLM4624_0010201.jpg',
    'I1NLM4624_0010202.jpg',
    'I1NLM4624_0010204.jpg',
    'I1NLM4649_0010094.jpg',
    'I1NLM4654_0010240.jpg',
    'I1NLM4667_0010162.jpg',
    'I1NLM5028_0010050.jpg',
    'I1NLM5103_0010290.jpg',
    'I1NLM5190_0010083.jpg',
    'I1NLM5190_0010111.jpg',
    'I1NLM5190_0010171.jpg',
    'I1NLM5190_0010172.jpg',
    'I1NLM5190_0010174.jpg',
    'I1NLM5190_0010376.jpg',
    'I1NLM5190_0010378.jpg',
    'I1NLM5190_0010381.jpg',
    'I1NLM5190_0010392.jpg',
    'I1NLM5190_0010398.jpg',
    'I1NLM5190_0010401.jpg',
    'I1NLM5431_0010234.jpg',
    'I1NLM5512_0010024.jpg',
    'I1NLM5512_0010026.jpg',
    'I1NLM5512_0010031.jpg',
    'I1NLM5523_0010070.jpg',
    'I1NLM5611_0010189.jpg',
]

NO_STAMP_TEXT_BREAK = [
    'I1NLM5561_0010135.jpg',
    'I1NLM1581_0010230.jpg',
    'I1NLM5009_0010029.jpg',
    'I1NLM4077_0010239.jpg',
    'I1NLM259_0010060.jpg'
]

TRIPLE = [
    'I1NLM4033_0010297.jpg',
    'I1NLM3990_0010126.jpg',
    "I1NLM446_0010147.jpg",
    "I1NLM481_0010061.jpg",
    "I1NLM481_0010064.jpg",
    "I1NLM481_0010066.jpg",
    "I1NLM481_0010067.jpg",
    'I1NLM481_0010068.jpg',
    "I1NLM1479_0010395.jpg",
    'I1NLM3990_0010126.jpg',
    'I1NLM3990_0010137.jpg',
    'I1NLM4004_0010215.jpg',
    'I1NLM5190_0010379.jpg'
]

QUAD = [
    'I1NLM5190_0010400.jpg',
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

def analyze_volume(batchdir, jsonlfn, stats, sort_for_false_positives, sort_for_false_negatives, sort_for_false_negatives_pos, not_very_high, grand_outline):
    basefn = jsonlfn[len(batchdir):-6]
    [wlname, ilname] = basefn.split("-")
    #if wlname != "W1NLM26":
    #    return
    vinfo = VINFO[ilname]
    nb_numbers_expected = vinfo["nb_texts"]
    images = get_images(jsonlfn)
    nb_detected = 0
    # sort from higher to lower
    #images = sorted(images, key=lambda x: x[1])
    positives = set()
    less_positives = set()
    nvh = set()
    nb_strikedthrough = 0
    nb_double = 0
    nb_triple = 0
    nb_quad = 0
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
        if "" in from_training:
            print("woooooo")
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
        if img in QUAD:
            nb_quad += 1
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
    #not_very_high+=list(nvh)
    positives = sorted(list(positives))
    add_to_grand_outline(grand_outline, wlname, ilname, positives)
    nb_detected = len(positives) - nb_strikedthrough + nb_double + 2 * nb_triple + 3 * nb_quad
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
        #create_outline(wlname, ilname, positives)
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

def add_to_grand_outline(grand_outline, wlname,ilname,positives):
    numbers = VINFO[ilname]["numbers"]
    spos = sorted(list(positives))
    img_i = 0
    number_i = 0
    adjust = 0
    for img in positives:
        if img in IRREGULARITY_BEFORE:
            adjust += 1
        elif img in STRIKEDTHROUGH or img in DUPLICATES or img in IGNORE:
            adjust -= 1
        elif img in DOUBLE:
            adjust += 1
        elif img in TRIPLE:
            adjust += 2
        elif img in QUAD:
            adjust += 3
    adjusted = len(numbers) == len(positives) + adjust
    adjustment_lost = False
    while img_i < len(spos) or number_i < len(numbers):
        img = "?"
        nb_numbers = 1
        if img_i < len(spos):
            img = spos[img_i][-8:-4].lstrip("0")
            if adjustment_lost:
                img += "?"
            if img in STRIKEDTHROUGH or img in DUPLICATES or img in IGNORE:
                img_i += 1
                continue
            if img_i > 0:
                grand_outline[-1][3] = img
            if img in DOUBLE:
                nb_numbers = 2
            elif img in TRIPLE:
                nb_numbers = 3
            elif img in QUAD:
                nb_numbers = 4
            if img in IRREGULARITY_BEFORE:
                if number_i < len(numbers):
                    grand_outline.append([wlname,numbers[number_i], "?",img])
                number_i += 1
                if not adjusted:
                    adjustment_lost = True
        else:
            grand_outline[-1][3] = "?"
        for j in range(nb_numbers):
            if number_i + j < len(numbers):
                grand_outline.append([wlname,numbers[number_i+j], img,img if j < nb_numbers -1 else "?"])
        img_i += 1
        number_i += nb_numbers

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
    #download_images(not_very_high, analysisdir+"nvh/")
    with open("grand_outline.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        for r in grand_outline:
            writer.writerow(r)

main("results/batch2/", "analyses/batch2/")