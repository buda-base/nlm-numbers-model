import os
import json
import numpy as np
import keras
import tensorflow as tf
from natsort import natsorted
from tqdm import tqdm
from glob import glob
import boto3
import botocore
import hashlib
import csv
from PIL import Image
import io
import logging

SESSION = boto3.Session()
S3 = SESSION.client('s3')

IMAGE_SIZE = 244

model_file = "Models/xce_model_1100.h5"
MODEL_NAME = os.path.basename(model_file).split(".")[0]
MODEL = keras.models.load_model(model_file)

OUT_PATH = "results/"+MODEL_NAME+"/"
if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

def batch_data(images, batch_size=8):
    if len(images) % batch_size == 0:
        num_batches = len(images) // batch_size
    else:
        num_batches = (len(images) // batch_size) + 1

    img_batches = np.array_split(images, num_batches)

    return img_batches

def get_sample():
    res = []
    with open("representative_samples.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            res.append(row[1])
    return res

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

def preprocess_image(imgfname):
    i = imgfname.find("_001")
    if i == -1:
        print("bug! %s" % imgfname)
    wlname = "W"+imgfname[1:i]
    ilname = imgfname[:i]+"_001"
    s3prefix = get_s3_folder_prefix(wlname, ilname)
    print(wlname)
    print(ilname)
    print(s3prefix)
    print(imgfname)
    img = Image.open(gets3blob(s3prefix+imgfname)).convert('L')
    img = tf.keras.utils.img_to_array(img)
    if img.shape[0] <= img.shape[1]:
        img = tf.slice(img, begin=[0, 0, 0], size=[tf.shape(img)[0], tf.shape(img)[0], 1])
    else:
        img = tf.slice(img, begin=[0, 0, 0], size=[tf.shape(img)[0], tf.shape(img)[0] // 2, 1])
    img = tf.image.resize_with_pad(
        img,
        target_height=IMAGE_SIZE,
        target_width=IMAGE_SIZE,
        method=tf.image.ResizeMethod.LANCZOS3,
    )
    img = tf.cast(img, tf.float32)
    img /= 255.0

    return img


def predict_batch(image_batch):
    images = [preprocess_image(x) for x in image_batch]
    images = np.array(images)
    batched_predictions = MODEL.predict_on_batch(images)

    return batched_predictions

def save_results(results):
    jsonl_string = ""

    for batched_results in results:
        for result in batched_results:
            json_string = json.dumps(
                result, ensure_ascii=False, separators=(", ", ": ")
            )
            jsonl_string += json_string + "\n"

    S3.put_object(
        Body=jsonl_string, 
        Bucket='image-processing.bdrc.io', 
        Key='nlm-numbers/Aresults/'+MODEL_NAME+"/samples.jsonl"
    )

def list_all_w():
    """
    lists everything with more than one text
    """
    res = []
    with open("nlm-volumeinfos.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)
        for row in reader:
            if int(row[3]) > 1:
                res.append((row[1], row[2]))
    return natsorted(res)

def run_imgfnamelist(imglist):
    batched_images = batch_data(imglist)
    accumulated_results = []

    for idx in range(0, len(batched_images)):
        predictions = predict_batch(batched_images[idx])
        results = np.stack(
            (
                batched_images[idx],
                np.round(predictions[:, 0], decimals=2),
                np.round(predictions[:, 1], decimals=2),
            ),
            axis=1,
        )
        accumulated_results.append(results.tolist())

    return accumulated_results


def run_everything():
    imglist = get_sample()
    results = None
    try:
        results = run_imgfnamelist(imglist)
    except Exception as e: 
        logging.exception(e)
    if results is not None:
        save_results(results)

if __name__ == "__main__":
    run_everything()