#!/usr/bin/env python
# Download IA maps and convert them to PDFs for printing

import sys, os, urllib
from PIL import Image

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

totalNumberOfMaps = 32

mapNumbers = range(1, totalNumberOfMaps+1)

# for mapNumber in mapNumbers:
#     fileURL = 'http://ibrahimshaath.co.uk/imperialassault/%02i.jpg' % mapNumber
#     print 'Downloading:', fileURL
#     urllib.urlretrieve(fileURL, os.path.split(fileURL)[1])

fileNumberIter = 1

print "\nDownloads done. Combining Images. This might take some processing time..."

for listOfMapNumsToCombine in chunks(mapNumbers, 6):
    jpgFile = 'map_group_%i.jpg' % fileNumberIter
    # For tournament maps use this name instead:
    # jpgFile = 'tournament_maps_%i.jpg' % fileNumberIter

    # For tournament maps just print these map numbers
    # if you want to make a custom selection of maps, you can enter them here too
    listOfMapNumsToCombine = [15, 19, 24]

    sourceList = []
    for i in listOfMapNumsToCombine:
        sourceList.append('%02i.jpg' % i)

    # combine images:
    images = map(Image.open, sourceList)
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height  = max(heights)

    # add 12 pixel border (24 pix on each dimension) to all sides for cutoff area
    # luckily, this is already black!
    combined_im = Image.new('RGB', (total_width + 24 , max_height + 24))

    x_offset = 12
    for im in images:
        combined_im.paste(im, (x_offset, 12))
        x_offset += im.size[0]

    # Save new image as a JPG
    combined_im.save( jpgFile, dpi=[300,300] )

    print "Print %s (on pixartprinting.com) at %s inches wide by %s inches tall (%s by %s cm)" % (jpgFile, total_width/300.0, max_height/300.0, total_width/300.0*2.54, max_height/300.0*2.54)

    fileNumberIter += 1

    # If you just want to print one page of stuff, eg for tournament maps, break here and don't loop
    # break
