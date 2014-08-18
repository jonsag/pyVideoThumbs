#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import ConfigParser, os, getopt, sys

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
infoHeight = int(config.get('contactsheets', 'infoHeight'))
sheetParams = [sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground, infoHeight]

startOffset = int(config.get('frameGrabbing', 'startOffset')) # parameters for the frame grabs
endOffset = int(config.get('frameGrabbing', 'endOffset'))
grabber = config.get('frameGrabbing', 'grabber')
frameFormat = config.get('frameGrabbing', 'frameFormat')
videoParams = [startOffset, endOffset, grabber, frameFormat]

timeCode = config.get('timeCode', 'timeCode')
tcPlace = config.get('timeCode', 'tcPlace')
tcColour = config.get('timeCode', 'tcColour')
tcOutlineColour = config.get('timeCode', 'tcOutlineColour')
tcFont = config.get('timeCode', 'tcFont')
tcSize = int(config.get('timeCode', 'tcSize'))
tcParams = [timeCode, tcPlace, tcColour, tcOutlineColour, tcFont, tcSize]

infoColour = config.get('info', 'infoColour')
infoOutlineColour = config.get('info', 'infoOutlineColour')
infoFont = config.get('info', 'infoFont')
infoSize = int(config.get('info', 'infoSize'))
infoParams = [infoColour, infoOutlineColour, infoFont, infoSize]

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

############### single video file ###############
if file:
    print "\n%s\n------------------------------------------------------------------" % file

    frameNames, grabTimes, fileInfo = generateFrames(file, videoParams, sheetParams, tempDir, info, verbose)

    contactSheet = makeContactSheet(frameNames, grabTimes, fileInfo, sheetParams, tcParams, infoParams, tempDir, verbose) # create the contact sheet

    fileName = os.path.basename(file)
    contactSheet.save("%s.png" % fileName) # save contact sheet
