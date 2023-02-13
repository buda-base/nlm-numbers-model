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

SESSION = boto3.Session()
S3 = SESSION.client('s3')

IMAGE_SIZE = 244

model_file = "Models/xce_model.h5"
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


def preprocess_image(img):
    img = tf.io.read_file(img)
    img = tf.io.decode_jpeg(img, channels=1)
    
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


def predict_batch(s3prefix, image_batch):
    images = [preprocess_image(s3prefix, x) for x in image_batch]
    images = np.array(images)
    batched_predictions = MODEL.predict_on_batch(images)

    return batched_predictions


def run_prediction(work_idx, write_output=True):
    work_path = os.path.join(NLM_DATA, WORKS[work_idx])
    work_images = natsorted(glob(f"{work_path}/*.jpg"))

    if len(work_images) != 0:
        batched_images = batch_data(work_images)
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

    else:
        return None


def save_results(results, w, model_name, out_path):
    json_file = f"{out_path}{w}.jsonl"

    with open(json_file, "w", encoding="utf8") as f:
        for batched_results in results:
            for result in batched_results:
                json_string = json.dumps(
                    result, ensure_ascii=False, separators=(", ", ": ")
                )
                f.write(f"{json_string}\n")

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

def get_image_list(w, i):
    res = []
    with open("imageinfos/"+w+"-"+i+".csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # we can skip the first two images, we already looked at those
        next(reader)
        next(reader)
        for row in reader:
            res.append(row[0])
    return res

def run_wi(w, i):
    s3prefix = get_s3_folder_prefix(w,i)
    imglist = get_image_list(w, i)
    #imglist = imglist[:1]
    batched_images = batch_data(imglist)
    accumulated_results = []

    for idx in range(0, len(batched_images)):
        predictions = predict_batch(s3prefix, batched_images[idx])
        results = np.stack(
            (
                batched_images[idx],
                np.round(predictions[:, 0], decimals=2),
                np.round(predictions[:, 1], decimals=2),
            ),
            axis=1,
        )
        print(results)
        accumulated_results.append(results.tolist())

    return accumulated_results


def run_everything():
    allw = list_all_w()
    for (w, i) in tqdm(allw):
        results = run_wi(w, i)
        if results is not None:
            save_results(results, w, MODEL_NAME, OUT_PATH)
        break

if __name__ == "__main__":
    run_everything()