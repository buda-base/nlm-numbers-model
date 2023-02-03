import csv
import urllib.request

imgwithstamps = []
for line in urllib.request.urlopen("http://www.rkts.org/NLM/data.php"):
    rows = line.decode('utf-8').split("<br>")
    for row in rows:
        l = row.split("###")
        if len(l) < 2:
            continue
        nlmnum = l[1].split(".")[0]
        imgnum = 0
        try:
            imgnum = int(l[2])
        except:
            continue
        imgfname = "I1"+nlmnum+"_001%04d.jpg" % imgnum
        imgwithstamps.append(imgfname)

imgwithstamps = sorted(imgwithstamps)
for img in imgwithstamps:
    print(img)