# Ground truth

## Potential issues

In rare cases, the cropping cut the stamp from the images, sometimes entirely, so that only the number is visible.

Since we only looked at the first two images of each volume, the training data is heavily skewed towards numbers ending in `-001` by construction.

## Files

#### allimages.csv

All the images that were used in the training data.

#### stamp_number.csv

images that have a stamp + number easy to read by a human.

#### difficult.csv

images that have a stamp + number but where it it difficult to see even for a human.

#### stamp_transparency.csv

images where the stamp of the other side of the folio is visible.

#### no_stamp.csv

images where no stamp or number is visible at all.