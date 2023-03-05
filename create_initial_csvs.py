import csv
import hashlib
import io
import boto3
import botocore
import gzip
import json
from pathlib import Path

# Script to create the initial csv files in imageinfos/
# Requires s3 credentials

SESSION = boto3.Session()
S3 = SESSION.client('s3')

def read_winfos():
    res = {}
    with open("nlm-volumeinfos.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            res[row[1]] = {
                "nlm_id": row[0],
                "i": row[2],
                "nb_texts": int(row[3])
            }
    return res

WINFOS = read_winfos()

def read_allw():
    res = {}
    with open("allw.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            res[row[0]] = row[1]
    return res

ALLW = read_allw()

def get_s3_folder_prefix(wlname, image_group_lname):
    """
    gives the s3 prefix (~folder) in which the volume will be present.
    inpire from https://github.com/buda-base/buda-iiif-presentation/blob/master/src/main/java/
    io/bdrc/iiif/presentation/ImageInfoListService.java#L73
    Example:
       - wlname=W22084, image_group_lname=I0886
       - result = "Works/60/W22084/images/W22084-0886/
    where:
       - 60 is the first two characters of the md5 of the string W22084
       - 0886 is:
          * the image group ID without the initial "I" if the image group ID is in the form I\\d\\d\\d\\d
          * or else the full image group ID (incuding the "I")
    """
    md5 = hashlib.md5(str.encode(wlname))
    two = md5.hexdigest()[:2]

    pre, rest = image_group_lname[0], image_group_lname[1:]
    if pre == 'I' and rest.isdigit() and len(rest) == 4:
        suffix = rest
    else:
        suffix = image_group_lname

    return 'Works/{two}/{RID}/images/{RID}-{suffix}/'.format(two=two, RID=wlname, suffix=suffix)

def gets3blob(s3Key):
    f = io.BytesIO()
    try:
        S3.download_fileobj('archive.tbrc.org', s3Key, f)
        return f
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return None
        else:
            raise

def get_image_list_s3(wlname, image_group_lname):
    s3key = get_s3_folder_prefix(wlname, image_group_lname)+"dimensions.json"
    blob = gets3blob(s3key)
    if blob is None:
        return None
    blob.seek(0)
    b = blob.read()
    ub = gzip.decompress(b)
    s = ub.decode('utf8')
    data = json.loads(s)
    return data

def create_initial_volume_csvs():
    global WINFOS

    seenw = []

    for w, winfo in WINFOS.items():
        seenw.append(w)
        if w not in ALLW:
            continue
        csvfname = 'imageinfos/'+w+'-'+winfo["i"]+'.csv'
        if Path(csvfname).is_file():
            print("skip "+csvfname)
            continue
        iil = get_image_list_s3(w, winfo["i"])
        if iil is None:
            print("cannot get image list for "+w)
            continue
        print("write "+csvfname)
        with open(csvfname, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            for i, imginfo in enumerate(iil):
                writer.writerow([imginfo["filename"], str(i+1), imginfo["width"], imginfo["height"]])

    for w, ig in ALLW.items():
        if w in seenw:
            continue
        csvfname = 'imageinfos/'+w+'-'+ig+'.csv'
        if Path(csvfname).is_file():
            print("skip "+csvfname)
            continue
        iil = get_image_list_s3(w, ig)
        if iil is None:
            print("cannot get image list for "+w)
            continue
        print("write "+csvfname)
        with open(csvfname, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            for i, imginfo in enumerate(iil):
                writer.writerow([imginfo["filename"], str(i+1), imginfo["width"], imginfo["height"]])

create_initial_volume_csvs()