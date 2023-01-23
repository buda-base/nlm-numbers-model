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
from pathlib import Path

# get ground truth images from the image processing S3 bucket
# requires s3 credentials

SESSION = boto3.Session()
S3 = SESSION.client('s3')

def get_images(name):
    csv_fname = "groundtruth/"+name+".csv"
    basedir = "groundtruth/"+name+"/"
    Path(basedir).mkdir(exist_ok=True)
    with open(csv_fname, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            imgfname = row[0]
            basename = imgfname[1:imgfname.find("_")]
            wlname = "W"+basename
            ilname = "I"+basename+"_001"
            s3key = "nlm-numbers/"+wlname+"-"+ilname+"/"+imgfname
            S3.download_file("image-processing.bdrc.io", s3key, basedir+imgfname)

get_images("no_stamp")
get_images("stamp_number")
get_images("stamp_transparency")