#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import ConfigParser, os, getopt, sys

from error import *
from video import *
from image import *
from misc import *

config = ConfigParser.ConfigParser() # define config file
config.read("%s/config.ini" % os.path.dirname(os.path.realpath(__file__))) # read config file

videoTypes = config.get('video', 'videoTypes') # allowed file types

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
    myopts, args = getopt.getopt(sys.argv[1:],'f:p:o:ivh' , ['file=', 'path=', 'outdir', 'info', 'verbose', 'help'])

except getopt.GetoptError as e:
    onError(1, str(e))

if len(sys.argv) == 1: # no options passed
    onError(2, 2)

file = ""
path = ""
outDir = ""
info = False
verbose = False
outDir = ""

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
    elif option in ('-o', '--outdir'):
        outDir = argument
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
    tempDir = makeDir(os.getcwd(), tempDir)
else:
    if not os.access(tempDir, os.W_OK):
        onError(8, tempDir)
if verbose:
    print "--- Temporary directory is %s" % tempDir

# checking out directory
if outDir and os.path.isdir(os.path.join(os.getcwd(), outDir)): # if directory exist in current path
    outDir = os.path.join(os.getcwd(), outDir)
elif file and outDir and os.path.isdir(os.path.join(os.path.dirname(file), outDir)): # if file and outdir is given and, outdir exist in files directory
    outDir = os.path.join(os.path.dirname(file), outDir)
elif file and outDir and not os.path.isdir(os.path.join(os.path.dirname(file), outDir)): # if file and outdir is given, and outdir does NOT exist in file's directory
    print "*** Out directory %s doesn't exist" % os.path.join(os.path.dirname(file), outDir)
    outDir = makeDir(os.path.dirname(file), outDir)
elif path and outDir and os.path.isdir(os.path.join(path, outDir)): # if path and outdir is given and outdir exist in path's directory
    outDir = os.path.join(path, outDir)
elif path and outDir and not os.path.isdir(os.path.join(path, outDir)): # if path and outdir is given and outdir does NOT exist in path's directory
    print "*** Out directory %s doesn't exist" % os.path.join(path, outDir)
    outDir = makeDir(path, outDir)
else:
    outDir = os.getcwd()

if verbose:
    print "--- Output directory is %s" % outDir

############### single video file ###############
if file:
    if checkIfVideo(file, videoTypes, verbose):
        frameNames, grabTimes, fileInfo = generateFrames(file, videoParams, sheetParams, tempDir, info, verbose)
        contactSheet = makeContactSheet(frameNames, grabTimes, fileInfo, sheetParams, tcParams, infoParams, tempDir, info, verbose) # create the contact sheet
        fileName = os.path.basename(file)
        contactSheet.save("%s/%s.png" % (outDir, fileName)) # save contact sheet
