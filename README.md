# nlm-numbers-model

Training data and code for a model to detect accession numbers in images from the National Library of Mongolia.

### Description of the project

The Buddhist Digital Resource Center (BDRC) is the main digitization partner of the National Library of Mongolia (NLM, for more, see [this blog post](https://www.bdrc.io/blog/2020/12/17/tibetan-treasures-from-the-national-library-of-mongolia/)). Scans of about 6,000 volumes are already openly accessible on the BDRC website [here](https://library.bdrc.io/show/bdr:PR1NLM00).

So far, BDRC only imported information on the first text of each volume, but this just a drop in the ocean since the NLM identified 70,000 different texts in these volumes. The catalog of these texts is accessible to BDRC but in order to import it properly, BDRC needs to map the titles with the images, a task that would take months or years to finish.

Fortunately, the NLM cataloguers wrote an accession number on the first page of each text, as exemplified in the following image:

![First page of an NLM volume](https://iiif.bdrc.io/bdr:I1NLM2739_001::I1NLM2739_0010001.jpg/full/max/0/default.jpg).

This project leverages AI to detect these numbers and automate the mapping from the NLM catalog to the images themselves.

### Creation of the data

`nlm-volumeinfos.csv` contains information about each volume of the NLM collection, including a list of all the numbers that should appear on the images. Note that the model does not need to be used on the 613 volumes having only one text. Warning: not all volumes have images yet.

The `imageinfos/` directory contains csv files named after each volume, listing the images in the volume with the following columns:
- the original image file name
- the BDRC image number
- width of the original image
- height of the original image

Since the NLM cataloguers seem to have been very consistent in the way they wrote the number, we prepare the image for processing by:
- cropping the right side (80% of the image)
- rotating the images 90° counter-clockwise

## Preparing the training data



obtaining a result similar to

1636 -> double number
3361, 3362, 4043 -> difficult
4402
2955,2965-2967,2984,2986,2989,3361,3366,3456,3597,3988,4722

difficult case: https://iiif.bdrc.io/bdr:I1NLM260_001::I1NLM260_0010013.jpg/full/max/0/default.jpg
https://iiif.bdrc.io/bdr:I1NLM58_001::I1NLM58_0010182.jpg/full/max/0/default.jpg

I1NLM232_0010162.jpg

I1NLM24_0010173.jpg should have a stamp and number but doesn't
I1NLM6_0010214.jpg
I1NLM6_0010298.jpg

outline missing: 1354

I1NLM2119_0010022

scanned twice: I1NLM2261_0010187
barred: I1NLM3081_0010104, I1NLM3486_0010199, I1NLM3852_0010276, I1NLM3870_0010013, I1NLM3870_0010037, I1NLM4202_0010064, I1NLM4191_0010116, I1NLM4246_0010209, I1NLM4316_0010040, I1NLM4669_0010324, I1NLM5148_0010293, I1NLM5329_0010257, I1NLM5414_0010157, I1NLM3478_0010169, I1NLM3486_0010199, I1NLM3645_0010259, I1NLM3852_0010276
double: I1NLM3870_0010041, I1NLM2801_0010239, I1NLM2801_0010330
strange: I1NLM4038_0010001

weird case: I1NLM511_0010366, I1NLM511_0010367