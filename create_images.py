import csv
import hashlib
import io
import boto3
import botocore
import gzip
import json
from pathlib import Path
import PIL
from PIL import Image as PillowImage
from tqdm import tqdm
from glob import glob
import logging
import statistics

# get images from the BDRC s3 archive,
# process them and upload on s3://image-processing.bdrc.io/nlm-numbers/
# requires s3 credentials

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
        f.seek(0)
        return f
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return None
        else:
            raise

def get_med_height():
    heights = []
    csv_files = sorted(glob("./imageinfos/*.csv"))
    for csv_fname in tqdm(csv_files):
        with open(csv_fname, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                heights.append(int(row[3]))
    print(statistics.median(heights))
    print(statistics.mean43(heights))

TARGET_WIDTH = 450
TARGET_HEIGHT = 250

def process_image(wlname, ilname, imgfname):
    sources3key = get_s3_folder_prefix(wlname, ilname)+imgfname
    blob = gets3blob(sources3key)
    if blob is None:
        logging.exception(f"Failed to read {s3key} from s3")
        return None
    try:
        img = PillowImage.open(blob)
    except Exception:
        logging.exception(f"Failed to read {s3key} with Pillow")
        return False
    width, height = img.size
    if height != TARGET_WIDTH:
        new_width = int(width * TARGET_WIDTH / height)
        img = img.resize((new_width, TARGET_WIDTH), PIL.Image.Resampling.LANCZOS)
    #if height < TARGET_WIDTH:
    #    new_img = PIL.Image.new(img.mode, (img.width, TARGET_WIDTH), (0,0,0))
    #    new_img.paste(img, (0, int(height - TARGET_WIDTH /2)))
    #    img = new_img
    img = img.crop((0, 0, TARGET_HEIGHT, img.height))
    img = img.rotate(90, expand=1)
    dests3key = "nlm-numbers/"+wlname+"-"+ilname+"/"+imgfname
    #img.save(imgfname, "JPEG", progressive=True, optimize=True)
    # Save the image to an in-memory file
    in_mem_file = io.BytesIO()
    img.save(in_mem_file, "JPEG", progressive=True, optimize=True)
    in_mem_file.seek(0)
    S3.upload_fileobj(
        in_mem_file, # This is what i am trying to upload
        "image-processing.bdrc.io",
        dests3key,
    )

# test
#get_med_height()
#process_image("W1NLM22", "I1NLM22_001", "I1NLM22_0010002.jpg")
#process_image("W1NLM102", "I1NLM102_001", "I1NLM102_0010030.jpg")
#process_image("W1NLM1052", "I1NLM1052_001", "I1NLM1052_0010001.jpg")
#process_image("W1NLM1095", "I1NLM1095_001", "I1NLM1095_0010029.jpg")


def process_all_csvs():
    csv_files = sorted(glob("./imageinfos/*.csv"))
    for csv_fname in tqdm(csv_files):
        [wlname, ilname] = csv_fname[13:].split("-")
        ilname = ilname[:-4]
        winfo = WINFOS[wlname]
        with open(csv_fname, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            row_i = 0
            for row in reader:
                row_i += 1
                if row_i > 2:# and winfo["nb_texts"] < 2:
                    # no need to process images for volumes with just one text
                    break
                imgfname = row[0]
                try:
                    process_image(wlname, ilname, imgfname)
                except KeyboardInterrupt as e:
                    raise e
                except:
                    logging.exception("error while processing "+csv_fname)

process_all_csvs()