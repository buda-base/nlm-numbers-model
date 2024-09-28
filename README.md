# nlm-numbers-model

Training data and code for a model to detect accession numbers in images from the National Library of Mongolia.

### Description of the project

The Buddhist Digital Resource Center (BDRC) is the main digitization partner of the National Library of Mongolia (NLM, for more, see [this blog post](https://www.bdrc.io/blog/2020/12/17/tibetan-treasures-from-the-national-library-of-mongolia/)). Scans of about 6,000 volumes are already openly accessible on the BDRC website [here](https://library.bdrc.io/show/bdr:PR1NLM00).

So far, BDRC only imported information on the first text of each volume, but this just a drop in the ocean since the NLM identified 70,000 different texts in these volumes. The catalog of these texts is accessible to BDRC but in order to import it properly, BDRC needs to map the titles with the images, a task that would take months or years to finish.

Fortunately, the NLM cataloguers wrote an accession number on the first page of each text, as exemplified in the following image:

![First page of an NLM volume](https://iiif.bdrc.io/bdr:I1NLM2739_001::I1NLM2739_0010001.jpg/full/max/0/default.jpg).

This project leverages AI to detect these numbers and automate the mapping from the NLM catalog to the images themselves.

### Creation of the data (BDRC)

`nlm-volumeinfos.csv` contains information about each volume of the NLM collection, including a list of all the numbers that should appear on the images. Note that the model does not need to be used on the 613 volumes having only one text. Warning: not all volumes have images yet.

The `imageinfos/` directory contains csv files named after each volume, listing the images in the volume with the following columns:
- the original image file name
- the BDRC image number
- width of the original image
- height of the original image

Since the NLM cataloguers seem to have been very consistent in the way they wrote the number, we prepare the image for processing by:
- cropping the right side (80% of the image)
- rotating the images 90° counter-clockwise

## Running the inference (BDRC)

When a new batch of scans become available:

add the results of the following query to `allw.csv`:

```sparql
select ?w ?i {
  ?w :inCollection bdr:PR1NLM00 .
  FILTER(strstarts(str(?w), 'http://purl.bdrc.io/resource/W1NLM'))
  ?wadm adm:adminAbout ?w ;
        adm:status bda:StatusReleased .
  ?w :instanceHasVolume ?i .
  ?i :volumePagesTotal ?vpt .
  FILTER(?vpt > 2)
}
```

run `create_initial_csvs.py`

run `nlm-numbers-private/create-ai-dataset.py` and copy `nlm-volumeinfos.csv` in this repository.

Put the total number of images for each volume in `w-vpt.csv`, this can be done through the following query:

```sparql
select ?w ?vpt {
  ?w :inCollection bdr:PR1NLM00 .
  FILTER(strstarts(str(?w), 'http://purl.bdrc.io/resource/W1NLM'))
  ?wadm adm:adminAbout ?w ;
        adm:status bda:StatusReleased .
  ?w :instanceHasVolume ?i .
  ?i :volumePagesTotal ?vpt .
  FILTER(?vpt > 2)
}
``` 

run `nlm_classifier_infer.py` on a machine with GPU, and copy the new files in `s3://image-processing.bdrc.io/nlm-numbers/Aresults/xce_model/` in a directory in `results/`.


## Analyzing the results (BDRC or ALL)

run `analyze-results.py` a few times (TODO), looking at the different lists for debug. 

This produces two files:

- `outline.csv` with the image numbers for all the volumes where the number of detected stamps matches the number of texts in the catalog
- `outline_needs_review.csv` with the best approximation of image numbers for the volumes where the number of detected stamps is different from the number of texts in the catalog

These two files should then be copied into `nlm-numbers-private`.
