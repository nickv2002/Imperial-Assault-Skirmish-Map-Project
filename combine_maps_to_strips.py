#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Convert 300 DPI Maps to PDF strips for printing
# Requires Python 3 Pillow image processing libraries

import sys, os
from PIL import Image

def mkdir_p(path):
    import errno
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

# build a dictionary of all groups of maps to print
mapDict = {
    'Core':                                  [1,2,3,4,5,6,7,8,9,10],
    'TwinShadows':                           [11,12,13,14],
    'ReinforcementWave1WookiesHiredGuns':    [15,16,17],
    'ReturnToHoth':                          [18,19,20,21,22],
    'ReinforcementWave2BanthaSmuggler':      [23,24],
    'BespinGambit':                          [25,26,27,28,29],
    'ReinforcementWave3ObiGreedoGI':         [30,31,32],
    'JabbasRealm':                           [33,34,35,36,37],
    'ReinforcementWave4Droids':              [38,39,40],
    'HeartOfTheEmpire':                      [41,42,43,44],
    'TyrantsOfLothal':                       [45,46,47,48,49],
    'TournamentRotationUscruTarkinLothal':   [42,38,45],
     }
mapDictWidths = {} # we'll fill this later

# output directory
outputDir = "Combined_IA_Map_Sheets"

maxWidthInches = 108 # maxWidth of a strip in inches (based on Printi limits)
maxWidthPixels = maxWidthInches * 300.0 # assuming 300 DPI

# build the all map group from all numbers listed above, and index our pixel widths
allMapsNums = set()
for ithGroup in mapDict:
    for mapInt in mapDict[ithGroup]:
        mapFilename = os.path.join('IA_300_DPI_Skirmish_Maps', '%02i.jpg' % mapInt)
        assert os.path.isfile(mapFilename), "\nERROR: missing map: %s" % mapFilename
        allMapsNums.add( int(mapInt) )
        ithWidth, ithHeight = Image.open(mapFilename).size
        assert ithHeight/300. == 24.0, "\nERROR: unexpected map height of %s inches for %s" % (ithHeight/300, mapFilename)
        assert ithWidth > 4000, "\nERROR: very narrow map(?): %s" % mapFilename
        mapDictWidths[mapInt] = ithWidth
mapDict['All2PlayerMaps'] = sorted(allMapsNums)

for ithGroup in mapDict:
    # for just updating the All2PlayerMaps group:
    # if ithGroup != 'All2PlayerMaps': continue

    listOfMapsInGroup = mapDict[ithGroup]
    print("Working on: %s with %i maps" % (ithGroup, len(listOfMapsInGroup)))
    # make the output directory
    mkdir_p(os.path.join(outputDir, ithGroup))

    # Set up some variables for this loop
    placedList                    = []
    mapIntIter                    = 99999999 # to hit exception at start of while loop
    listOfGroupToCombineFor1Sheet = []
    doFirstGroupCreation          = False # to skip saving at intial exception

    while len(placedList) < len(listOfMapsInGroup):
        try: # to match the iter with the map number
            mapInt = listOfMapsInGroup[mapIntIter]
        except IndexError: # we iterated too high, save the group we just made, then restart a new sheet
            if doFirstGroupCreation:
                # print "created sheet", groupToCombineFor1Sheet
                listOfGroupToCombineFor1Sheet.append(groupToCombineFor1Sheet)
            doFirstGroupCreation    = True
            groupToCombineFor1Sheet = []
            widthPixelsCnt          = 0
            mapIntIter              = 0
            mapInt                  = listOfMapsInGroup[mapIntIter]

        if mapInt in placedList: # already placed, iterate higher
            pass
        elif widthPixelsCnt + mapDictWidths[mapInt] < maxWidthPixels: #placeable
            widthPixelsCnt += mapDictWidths[mapInt]
            # print "Place map # %i" % mapInt
            placedList.append(mapInt)
            groupToCombineFor1Sheet.append(mapInt)
        mapIntIter += 1
    # we need to create the last sheet (this may also be the first sheet for small groups)
    listOfGroupToCombineFor1Sheet.append(groupToCombineFor1Sheet)

    # print "Grouped the following maps together:", listOfGroupToCombineFor1Sheet

    # Set up some variables for this loop
    metadataList   = []
    fileNumberIter = 1

    for groupToCombineFor1Sheet in listOfGroupToCombineFor1Sheet:
        sourceJPGfilenamesList = []
        for mapInt in groupToCombineFor1Sheet:
            sourceJPGfilenamesList.append(os.path.join('IA_300_DPI_Skirmish_Maps', '%02i.jpg' % mapInt))

        outputFile = os.path.join(outputDir, ithGroup, '%s_%i.pdf' % (ithGroup, fileNumberIter))
        print("Creating:", outputFile)
        fileNumberIter += 1 # for next group

        # combine images:
        images = list(map(Image.open, sourceJPGfilenamesList))
        widths, heights = list(zip(*(i.size for i in images)))
        total_width   = sum(widths)
        max_height    = max(heights)
        assert total_width <= 108*300, 'ERROR: Printi max is 108 inches, but this section would be %s inches' % (total_width/300.0)
        assert max_height == 7200, 'ERROR: map height dimiensions are not what we expected: %s' % max_height

        # add 2 pixels of white between each map to help with cutting them apart
        combined_size = (total_width - 2 + len(sourceJPGfilenamesList) * 2, max_height)
        combined_im = Image.new('RGB', combined_size, color = (255,255,255))
        x_offset = 0
        for im in images:
            combined_im.paste(im, (x_offset, 0))
            x_offset += im.size[0] + 2 #add 2 pixels for division

        # Save new image as a PDF
        combined_im.save( outputFile, dpi=[300,300], quality = 85, resolution = 300.)

        # Save metadata tupal
        metadataList.append( (os.path.split(outputFile)[1], total_width/300., max_height/300., total_width/300.*2.54, max_height/300.*2.54) )

    with open(os.path.join(outputDir, ithGroup, 'ReadMe.md'), "w") as TF:
        for mdT in metadataList:
            TF.write('* Print `%s` at %s inches wide by %s inches tall (%s by %s cm)\n' % mdT)
        TF.write('\n#### Notes\n')
        TF.write('* Recommended shop & product: [Printi PVC Banners](https://www.printi.com/setup-banners-and-mesh)\n')
        TF.write('* The PDF files are very large so some people have trouble seeing them on their computer. Give them some time to display if you have an older computer\n')
        TF.write('* Questions? See the [GitHub project page](https://github.com/nickv2002/Imperial-Assault-Skirmish-Map-Project)')

    # for testing
    # break

# useful ImageMagic commands
# for i in `ls -d *.jpg`;do echo $i; identify -format "%y" $i; echo; done
# convert -units PixelsPerInch FourPlayer.jpg -density 300 300.FourPlayer.jpg
# identify -format "%w x %h %x x %y" image300.jpg
