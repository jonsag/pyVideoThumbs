#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import ConfigParser, os, getopt, sys, shlex

from subprocess import call, check_output, Popen, PIPE

from PIL import Image

from error import *
from video import *
from image import *

config = ConfigParser.ConfigParser() # define config file
config.read("%s/config.ini" % os.path.dirname(os.path.realpath(__file__))) # read config file

sheetWidth = int(config.get('contactsheets', 'sheetWidth')) # paramaters for the contact sheet
sheetHeight = int(config.get('contactsheets', 'sheetHeight'))
sheetColumns = int(config.get('contactsheets', 'sheetColumns'))
sheetRows = int(config.get('contactsheets', 'sheetRows'))
leftMargin = int(config.get('contactsheets', 'leftMargin'))
topMargin = int(config.get('contactsheets', 'topMargin'))
rightMargin = int(config.get('contactsheets', 'rightMargin'))
bottomMargin = int(config.get('contactsheets', 'bottomMargin'))
thumbPadding = int(config.get('contactsheets', 'thumbPadding'))
sheetBackground = config.get('contactsheets', 'sheetBackground')
sheetParams = [sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground]

startOffset = int(config.get('frameGrabbing', 'startOffset')) # parameters for the frame grabs
endOffset = int(config.get('frameGrabbing', 'endOffset'))
grabber = config.get('frameGrabbing', 'grabber')
frameFormat = config.get('frameGrabbing', 'frameFormat')
videoParams = [startOffset, endOffset, grabber, frameFormat]

tempDir = os.path.join(os.path.expanduser("~"), config.get('paths','tempDir')) # temporary dir, used to store frame grabs

############### handle arguments ###############
try:
    myopts, args = getopt.getopt(sys.argv[1:],'f:p:ivh' , ['file=', 'path=', 'info', 'verbose', 'help'])

except getopt.GetoptError as e:
    onError(1, str(e))

if len(sys.argv) == 1: # no options passed
    onError(2, 2)

file = ""
path = ""
info = False
verbose = False

for option, argument in myopts:
    if option in ('-f', '--file'):
        file = argument
        if not os.path.isfile(file):
            onError(4, file)
        elif os.path.islink(file):
            onError(5, file)
    elif option in ('-p', '--path'):
        path = argument
        if not os.path.isdir(path):
            onError(6, path)
    elif option in ('-i', '--info'):
        info = True
    elif option in ('-v', '--verbose'):
        verbose = True
    elif option in ('-h', '--help'):
        usage(0)
    else:
        onError(7, 7)

if file and path:
    onError(7, 7)

# checking temporary directory
if not os.path.isdir(tempDir):
    print "Temporary directory %s does not exist" % tempDir
    while True:
        createTempDir = raw_input('Do you want to create it? (Y/n)')
        if createTempDir.lower() == "y" or not createTempDir:
            os.makedirs(tempDir)
            break
        elif createTempDir.lower() == "n":
            onError(7, tempDir)

else:
    if not os.access(tempDir, os.W_OK):
        onError(8, tempDir)

if verbose:
    print "--- Temporary directory is %s" % tempDir

def makeContactSheet(frameNames, (sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground), verbose):
    sampleFrame = Image.open(frameNames[0])
    thumbWidth, thumbHeight = sampleFrame.size
    if verbose:
        print "--- Thumbs width x height: %s x %s" % (thumbWidth, thumbHeight)

    thumbs = [Image.open(frame).resize((thumbWidth, thumbHeight)) for frame in frameNames] # Read in all images and resize appropriately

    marginsWidth = leftMargin + rightMargin # Calculate the size of the output image, based on the photo thumb sizes, margins, and padding
    marginsHeight = topMargin + bottomMargin

    paddingsWidth = (sheetColumns - 1) * thumbPadding
    paddingsHeight = (sheetRows - 1) * thumbPadding
    contactSheetSize = (sheetColumns * thumbWidth + marginsWidth + paddingsWidth, sheetRows * thumbHeight + marginsHeight + paddingsHeight)

    contactSheet = Image.new('RGB', contactSheetSize, "rgb%s" % sheetBackground) # Create the new image

    # Insert each thumb:
    for rowNo in range(sheetRows):
        for columnNo in range(sheetColumns):
            left = leftMargin + columnNo * (thumbWidth + thumbPadding)
            right = left + thumbWidth
            upper = topMargin + rowNo * (thumbHeight + thumbPadding)
            lower = upper + thumbHeight
            bbox = (left, upper, right, lower)
            try:
                image = thumbs.pop(0)
            except:
                break
            contactSheet.paste(image, bbox)
    return contactSheet

############### single video file ###############
if file:
    print "\n%s\n------------------------------------------------------------------" % file
    frameNames = generateFrames(file, videoParams, sheetParams, tempDir, info, verbose)

    contactSheet = makeContactSheet(frameNames, sheetParams, verbose) # create the contact sheet                                                                                    
    contactSheet.save('bs.png') # save contact sheet
