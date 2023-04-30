#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import getopt
import os
import sys

# from misc import makeDir
# from error import usage, onError
# from video import checkIfVideo, generateFrames
# from image import makeContactSheet

from error import onError, usage
from misc import (makeDir, confirm,
                  tempDir, videoTypes,
                  videoParams, sheetParams, tcParams, infoParams)
from video import checkIfVideo, generateFrames, findVideos
from image import makeContactSheet

############### handle arguments ###############
try:
    myopts, args = getopt.getopt(sys.argv[1:], 'f:p:o:skrivh',
                                 ['file=',
                                  'path=',
                                  'outdir',
                                  'skipexisting',
                                  'keepgoing',
                                  'rename',
                                  'info',
                                  'verbose',
                                  'help'])

except getopt.GetoptError as e:
    onError(1, str(e))

if len(sys.argv) == 1:  # no options passed
    onError(2, "No options given")

myFile = ""
path = ""
outDir = ""
skipExisting = False
info = False
verbose = False
keepGoing = False
noRename = True
outDir = ""

for option, argument in myopts:
    if option in ('-f', '--file'):
        myFile = argument
        if not os.path.isfile(myFile):
            onError(4, "File %s does not exist" % myFile)
        elif os.path.islink(myFile):
            onError(5, "%s is a link" % myFile)
    elif option in ('-p', '--path'):
        path = argument
        if not os.path.isdir(path):
            onError(6, "%s is not a directory" % path)
    elif option in ('-o', '--outdir'):
        outDir = argument
    elif option in ('-s', '--skipexisting'):
        skipExisting = True
    elif option in ('-k', '--keepgoing'):
        keepGoing = True
    elif option in ('-r', '--rename'):
        if confirm("rename files", verbose):
            noRename = False
        else:
            print("--- Restart without rename option")
            sys.exit(0)
    elif option in ('-i', '--info'):
        info = True
    elif option in ('-v', '--verbose'):
        verbose = True
    elif option in ('-h', '--help'):
        usage(0)
    else:
        onError(11, "Option %s not recognised" % option)

if myFile and path:
    onError(7, "You can not set both -f and -p")

# checking temporary directory
if not os.path.isdir(tempDir):
    print("Temporary directory %s does not exist" % tempDir)
    tempDir = makeDir(os.getcwd(), tempDir)
else:
    if not os.access(tempDir, os.W_OK):
        onError(8, "Temporary directory %s not writeable" % tempDir)
if verbose:
    print("--- Temporary directory is %s" % tempDir)

# checking out directory
# if directory exist in current path
if outDir and os.path.isdir(os.path.join(os.getcwd(), outDir)):
    outDir = os.path.join(os.getcwd(), outDir)
# if file and outdir is given and, outdir exist in files directory
elif myFile and outDir and os.path.isdir(os.path.join(os.path.dirname(myFile), outDir)):
    outDir = os.path.join(os.path.dirname(myFile), outDir)
# if file and outdir is given, and outdir does NOT exist in file's directory
elif myFile and outDir and not os.path.isdir(os.path.join(os.path.dirname(myFile), outDir)):
    print("*** Out directory %s doesn't exist" %
          os.path.join(os.path.dirname(myFile), outDir))
    outDir = makeDir(os.path.dirname(myFile), outDir)
# if path and outdir is given and outdir exist in path's directory
elif path and outDir and os.path.isdir(os.path.join(path, outDir)):
    outDir = os.path.join(path, outDir)
# if path and outdir is given and outdir does NOT exist in path's directory
elif path and outDir and not os.path.isdir(os.path.join(path, outDir)):
    print("*** Out directory %s doesn't exist" % os.path.join(path, outDir))
    outDir = makeDir(path, outDir)
else:
    outDir = os.getcwd()

if verbose:
    print("--- Output directory is %s" % outDir)

############### single video file ###############
if myFile:
    if checkIfVideo(myFile, videoTypes, verbose):
        frameNames, grabTimes, fileInfo = generateFrames(myFile,
                                                         videoParams,
                                                         sheetParams,
                                                         tempDir,
                                                         keepGoing,
                                                         info, verbose)
        if frameNames:
            contactSheet = makeContactSheet(frameNames, grabTimes, fileInfo,
                                            sheetParams,
                                            tcParams,
                                            infoParams,
                                            tempDir,
                                            info, verbose)  # create the contact sheet

            fileName = os.path.basename(myFile)
            contactSheet.save("%s/%s.png" %
                              (outDir, fileName))  # save contact sheet
        else:
            print("*** Could not grab any frames\n    Skipping video")

############### scan path ###############
if path:
    videoNo = 0

    foundVideos = findVideos(
        path, videoTypes, keepGoing, noRename, outDir, verbose)

    foundVideos = sorted(foundVideos)
    noVideos = len(foundVideos)

    for myFile in foundVideos:
        videoNo += 1
        print("\n%s/%s" % (videoNo, noVideos))
        print("%s" % myFile)
        print("-" * 40)
        frameNames, grabTimes, fileInfo = generateFrames(myFile,
                                                         videoParams,
                                                         sheetParams,
                                                         tempDir,
                                                         keepGoing,
                                                         info, verbose)

        if frameNames:
            contactSheet = makeContactSheet(frameNames, grabTimes, fileInfo,
                                            sheetParams,
                                            tcParams,
                                            infoParams,
                                            tempDir,
                                            info, verbose)  # create the contact sheet
            fileName = os.path.basename(myFile)
            contactSheet.save("%s/%s.png" %
                              (outDir, fileName))  # save contact sheet
        else:
            print("*** Could not grab any frames\n    Skipping this video")
