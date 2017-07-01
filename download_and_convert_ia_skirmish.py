#!/usr/bin/env python
# coding=utf-8

# Convert 300 DPI Maps to JPGs strips for printing on PixArtPrinting

import sys, os
from PIL import Image

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

def mkdir_p(path):
    import errno
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

# output directory
outputDir = "Combined_IA_Map_Sheets"

# build a dictionary of all groups of maps to print
mapDict = {
    'Core':                                [1,2,3,4,5,6,7,8,9,10],
    'TwinShadows':                         [11,12,13,14],
    'ReinforcementWave1WookiesHiredGuns':  [15,16,17],
    'ReturnToHoth':                        [18,19,20,21,22],
    'ReinforcementWave2BanthaSmuggler':    [23,24],
    'BespinGambit':                        [25,26,27,28,29],
    'ReinforcementWave3ObiGreedoGI':       [30,31,32],
    'JabbasRealmIncomplete':               [37],
    # 'JabbasRealm':                         [33,34,35,36,37], #full set is not finished yet
    'ReinforcementWave4Droids':            [38,39,40],
    'TournamenRotationISBAnchorheadJabba': [27,30,37] }

# build the all map group from all numbers listed above
allMapsNums = set()
for ithGroup in mapDict:
    for mapInt in mapDict[ithGroup]:
        mapFilename = os.path.join('IA_300_DPI_Skirmish_Maps', '%02i.jpg' % mapInt)
        assert os.path.isfile(mapFilename), "\nERROR: missing map: %s" % mapFilename
        allMapsNums.add( int(mapInt) )
# mapDict['All2PlayerMaps'] = sorted(allMapsNums)

# Old system where we just downlaoded and iterate through the maps sequentially
#
# import urllib
# totalNumberOfMaps = 32
# mapNumbers = range(1, totalNumberOfMaps+1)
# for mapNumber in mapNumbers:
#     if not os.path.isfile('%02i.jpg' % mapNumber):
#         fileURL = 'http://ibrahimshaath.co.uk/imperialassault/%02i.jpg' % mapNumber
#         print 'Downloading:', fileURL
#         urllib.urlretrieve(fileURL, os.path.split(fileURL)[1])
# print "\nDownloads done. Combining Images. This might take some processing time..."

maxMapsInGroup = 10
for ithGroup in mapDict:
    # for testing
    # if ithGroup != 'All2PlayerMaps': continue
    listOfMapsInGroup = mapDict[ithGroup]
    multipleSheetsInGroup  = len(listOfMapsInGroup) > maxMapsInGroup
    fileNumberIter         = 1
    mkdir_p(os.path.join(outputDir, ithGroup))

    metadataList = []
    for listOfMapNumsToCombine in chunks(listOfMapsInGroup, maxMapsInGroup):
        if multipleSheetsInGroup:
            jpgFile = '%s_%i.jpg' % (ithGroup, fileNumberIter)
        else:
            jpgFile = '%s.jpg' % ithGroup
        jpgFile = os.path.join(outputDir, ithGroup, jpgFile)
        print "Creating:", jpgFile

        sourceList = []
        for mapInt in listOfMapNumsToCombine:
            sourceList.append(os.path.join('IA_300_DPI_Skirmish_Maps', '%02i.jpg' % mapInt))

        # combine images:
        images = map(Image.open, sourceList)
        widths, heights = zip(*(i.size for i in images))
        total_width   = sum(widths)
        max_height    = max(heights)
        assert max_height == 7200, 'ERROR map height dimiensions are not what we expected: %s' % max_height

        # add 2 pixels of white between each map to help with cutting them apart
        combined_size = (total_width - 2 + len(listOfMapNumsToCombine) * 2, max_height)
        combined_im = Image.new('RGB', combined_size, color = (255,255,255))
        x_offset = 0
        for im in images:
            combined_im.paste(im, (x_offset, 0))
            x_offset += im.size[0] + 2 #add 2 pixels for division

        # Save new image as a JPG
        combined_im.save( jpgFile, dpi=[300,300] )

        # Save metadata tupal
        metadataList.append( (os.path.split(jpgFile)[1], total_width/300.0, max_height/300.0, total_width/300.0*2.54, max_height/300.0*2.54) )

        # for next group
        fileNumberIter += 1

    with open(os.path.join(outputDir, ithGroup, 'ReadMe.md'), "w") as TF:
        for mdT in metadataList:
            TF.write('* Print `%s` at %s inches wide by %s inches tall (%s by %s cm)\n' % mdT)
        TF.write('\n#### Notes\n')
        TF.write('* Recommended shop & product: [PixArtPrinting PVC Banners](https://www.pixartprinting.com/signage/banners-mesh/pvc-banner/)\n')
        TF.write('* PixArtPrinting *does* print 300 DPI JPGs (created with this script) in addition to PDFs, even though they ask for PDFs initially.\n')
        TF.write('* The JPG files are very large so some people have trouble seeing them on their computer. Give them some time if you have an older computer\n')
        TF.write('* Questions? See [Boardwars](http://boardwars.eu/ia-maps/) and [New Orders](https://neworders.xyz/imperial-assault-skirmish-map-project/)\n')

    # for testing
    # break
