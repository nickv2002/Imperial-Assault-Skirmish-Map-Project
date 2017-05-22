#!/usr/bin/env python
# coding=utf-8

# Download IA maps and convert them to PDFs for printing

import sys, os, urllib
from PIL import Image

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

totalNumberOfMaps = 32

mapNumbers = range(1, totalNumberOfMaps+1)

for mapNumber in mapNumbers:
    if not os.path.isfile('%02i.jpg' % mapNumber):
        fileURL = 'http://ibrahimshaath.co.uk/imperialassault/%02i.jpg' % mapNumber
        print 'Downloading:', fileURL
        urllib.urlretrieve(fileURL, os.path.split(fileURL)[1])

print "\nDownloads done. Combining Images. This might take some processing time..."

fileNumberIter = 1
for listOfMapNumsToCombine in chunks(mapNumbers, 8):
    jpgFile = 'map_group_%i.jpg' % fileNumberIter
    # For tournament maps use this name instead:
    jpgFile = 'tournament_maps_%i.jpg' % fileNumberIter

    # For tournament maps just print these map numbers
    # if you want to make a custom selection of maps, you can enter them here too
    listOfMapNumsToCombine = [27,30,37]

    sourceList = []
    for i in listOfMapNumsToCombine:
        sourceList.append('%02i.jpg' % i)

    # combine images:
    images = map(Image.open, sourceList)
    widths, heights = zip(*(i.size for i in images))
    total_width   = sum(widths)
    max_height    = max(heights)

    # add 2 pixels of white between each map to help with cutting them apart
    combined_size = (total_width - 2 + len(listOfMapNumsToCombine) * 2, max_height)
    combined_im = Image.new('RGB', combined_size, color = (255,255,255))
    x_offset = 0
    for im in images:
        combined_im.paste(im, (x_offset, 0))
        x_offset += im.size[0] + 2 #add 2 pixels for division

    # Save new image as a JPG
    combined_im.save( jpgFile, dpi=[300,300] )

    print "Print %s (on pixartprinting.com) at %s inches wide by %s inches tall (%s by %s cm)" % (jpgFile, total_width/300.0, max_height/300.0, total_width/300.0*2.54, max_height/300.0*2.54)

    fileNumberIter += 1

    # If you just want to print one page of stuff, eg for tournament maps, break here and don't loop
    # break
