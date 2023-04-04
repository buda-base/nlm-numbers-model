import csv
from glob import glob
import json
from tqdm import tqdm
from create_images import get_processed_image
from pathlib import Path

def get_images(jsonlfn):
    res = []
    with open(jsonlfn, 'r') as json_file:
        for l in json_file:
            res.append(json.loads(l))
    return res

IMGTOTYPE = {}
def get_training_data():
    global IMGTOTYPE
    csv_fname = "representative_samples.csv"
    with open(csv_fname, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            IMGTOTYPE[row[1]] = row[0]

get_training_data()

def main(resfname):
    res = get_images(resfname)
    stats_new = {
        "true_positives": 0,
        "false_positives": 0,
        "true_negatives": 0,
        "false_negatives": 0,
    }
    stats_old = {
        "true_positives": 0,
        "false_positives": 0,
        "true_negatives": 0,
        "false_negatives": 0,
    }
    for imginfo in res:
        type_oldmodel = IMGTOTYPE[imginfo[0]]
        if type_oldmodel in ["tp", "ap"]:
            stats_old["true_positives"] += 1
        elif type_oldmodel in ["tn", "an"]:
            stats_old["true_negatives"] += 1
        elif type_oldmodel == "fn":
            stats_old["false_negatives"] += 1
        else:
            stats_old["false_positives"] += 1
        real_type = "p" if type_oldmodel in ["tp", "fn", "ap"] else "n"
        if float(imginfo[2]) < 0.5:
            if real_type == "p":
                stats_new["false_negatives"] += 1
            else:
                stats_new["true_negatives"] += 1
        else:
            if real_type == "n":
                stats_new["false_positives"] += 1
            else:
                stats_new["true_positives"] += 1
    precision_old = stats_old["true_positives"] / (stats_old["true_positives"] + stats_old["false_positives"])
    recall_old = stats_old["true_positives"] / (stats_old["true_positives"] + stats_old["false_negatives"])
    f_old = (2 * precision_old * recall_old) / (precision_old + recall_old)
    precision_new = stats_new["true_positives"] / (stats_new["true_positives"] + stats_new["false_positives"])
    recall_new = stats_new["true_positives"] / (stats_new["true_positives"] + stats_new["false_negatives"])
    f_new = (2 * precision_new * recall_new) / (precision_new + recall_new)
    print("old model: precision = %f, recall = %f, f = %f" % (precision_old, recall_old, f_old))
    print("new model: precision = %f, recall = %f, f = %f" % (precision_new, recall_new, f_new))

main("results/xce_model_1100/samples.jsonl")