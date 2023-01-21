# nlm-numbers-model

Training data and code for a model to detect accession numbers in images from the National Library of Mongolia.

### Description of the project

The Buddhist Digital Resource Center (BDRC) is the main digitization partner of the National Library of Mongolia (NLM, for more, see [this blog post](https://www.bdrc.io/blog/2020/12/17/tibetan-treasures-from-the-national-library-of-mongolia/)). Scans of about 6,000 volumes are already openly accessible on the BDRC website [here](https://library.bdrc.io/show/bdr:PR1NLM00).

So far, BDRC only imported information on the first text of each volume, but this just a drop in the ocean since the NLM identified 70,000 different texts in these volumes. The catalog of these texts is accessible to BDRC but in order to import it properly, BDRC needs to map the titles with the images, a task that would take months or years to finish.

Fortunately, the NLM cataloguers wrote an accession number on the first page of each text, as exemplified in the following image:

![First page of an NLM volume](https://iiif.bdrc.io/bdr:I1NLM2739_001::I1NLM2739_0010001.jpg/full/max/0/default.jpg).

This project leverages AI to detect these numbers and automate the mapping from the NLM catalog to the images themselves.

### Creation of the training data

`nlm-volumeinfos.csv` contains information about each volume of the NLM collection, including a list of all the numbers that should appear on the images.

The directory `imageinfos/` contains csv files named after each volume, listing the images in the volume with the following columns:
- the original image file name
- the BDRC image number
- width of the original image
- height of the original image
- "T" if a number is present on the image (in the golden standard), "F" if a number is not present, "" for no information
- same as previous but as the output of the model

