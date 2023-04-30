#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import os
import sys

from error import onError
from misc import checkFileName, contactSheetExist, executeCmd


def findVideos(path, videoTypes, keepGoing, noRename, outDir, verbose):
    foundVideos = []

    print("\n--- Searching %s for video files..." % path)
    for myFile in os.listdir(path):
        if checkIfVideo(myFile, videoTypes, verbose):
            print("\n--- Found: %s" % os.path.join(path, myFile))
            myFile = checkFileName(os.path.join(path, myFile),
                                   keepGoing, noRename,
                                   outDir, verbose)  # check if file name complies to rules
            if contactSheetExist(path, myFile, outDir, verbose):
                print("*** Contactsheet already exist\n    Skipping...")
            else:
                foundVideos.append(myFile)

    return foundVideos


def checkIfVideo(myFile, videoTypes, verbose):
    isVideo = False
    correctExtension = False

    if verbose:
        print("--- Checking %s" % myFile)

    extension = os.path.splitext(myFile)[1].lstrip('.')
    for myExtension in videoTypes:
        if extension.lower() == myExtension.strip(" ").lower():
            correctExtension = True
            break

    if correctExtension:
        if os.path.isfile and not os.path.islink(myFile) and not os.path.isdir(myFile):
            if verbose:
                print("--- This is not a link and is a valid video file")
            # print "\n%s\n------------------------------------------------------------------" % myFile
        isVideo = True

    return isVideo


def getVideoInfo(myFile, fileInfo, info, keepGoing, verbose):
    ##### general #####
    if verbose:
        print("--- Gathering general information...")
    cmd = "mediainfo %s '%s'" % (("--Inform=General;"
                                  "%Duration%,"
                                  "%Duration/String3%,"
                                  "%BitRate%,"
                                  "%BitRate/String%,"
                                  "%Format%,"
                                  "%FileSize%,"
                                  "%FileSize/String%,"
                                  "%StreamSize%,"
                                  "%StreamSize/String%,"
                                  "%FileName%,"
                                  "%FileExtension%"), myFile)

    output, error = executeCmd(cmd, verbose)
    if output == None and error == None:
        if keepGoing:
            print("*** Execution took too long")
        else:
            onError(13, "Execution took too long")

    answer = output.replace("\n", "").split(',')

    infoNo = 0
    for key in ("generalDurations",
                "generalDuration",
                "overallBitrates",
                "overallBitrate",
                "generalFormat",
                "fileSizeb",
                "fileSize",
                "generalStreamSizeb",
                "generalStreamSize",
                "fileName",
                "fileExtension"):
        try:
            fileInfo[key] = answer[infoNo]
        except:
            if not keepGoing:
                onError(15, "*** Could not get '%s'" % key)
            else:
                print("*** Could not get '%s'" % key)
            fileInfo[key] = "NA"
        infoNo += 1

    if info:
        fullFileName = "%s.%s" % (
            fileInfo['fileName'], fileInfo['fileExtension'])

        print("General:")
        print("File name: %s" % fullFileName)
        print("Duration: %s ms, %s" %
              (fileInfo['generalDurations'], fileInfo['generalDuration']))
        print("Overall bitrate: %s bps, %s" %
              (fileInfo['overallBitrates'], fileInfo['overallBitrate']))
        print("Format: %s" % fileInfo['generalFormat'])
        print("File size: %s b, %s" %
              (fileInfo['fileSizeb'], fileInfo['fileSize']))
        print("Stream size: %s b, %s" %
              (fileInfo['generalStreamSizeb'], fileInfo['generalStreamSize']))
        print(error)

    ##### video #####
    if verbose:
        print("--- Gathering video information...")

    cmd = "mediainfo %s '%s'" % (("--Inform=Video;"
                                  "%Duration%,"
                                  "%Duration/String3%,"
                                  "%Width%,"
                                  "%Height%,"
                                  "%BitRate%,"
                                  "%BitRate/String%,"
                                  "%FrameRate%,"
                                  "%FrameCount%,"
                                  "%Format%,"
                                  "%CodecID%,"
                                  "%PixelAspectRatio%,"
                                  "%DisplayAspectRatio%,"
                                  "%DisplayAspectRatio/String%,"
                                  "%Standard%,"
                                  "%StreamSize%,"
                                  "%StreamSize/String%"), myFile)

    output, error = executeCmd(cmd, verbose)
    if output == None and error == None:
        if keepGoing:
            print("*** Execution took too long")
        else:
            onError(13, "Execution took too long")

    answer = output.replace("\n", "").split(',')

    infoNo = 0
    for key in ("videoDurations",
                "videoDuration",
                "width",
                "height",
                "videoBitrateb",
                "videoBitrate",
                "frameRate",
                "frameCount",
                "videoFormat",
                "videoCodecID",
                "pixelAspectRatio",
                "displayAspectRatio",
                "displayAspectRatioTV",
                "tvStandard",
                "videoStreamSizeb",
                "videoStreamSize"):
        try:
            fileInfo[key] = answer[infoNo]
        except:
            if not keepGoing:
                onError(15, "*** Could not get '%s'" % key)
            else:
                print("*** Could not get '%s'" % key)
            fileInfo[key] = "NA"
        infoNo += 1

    if info:
        print("Video:")
        print("Duration: %s ms, %s" %
              (fileInfo['videoDurations'], fileInfo['videoDuration']))
        print("Width x height: %s x %s px" %
              (fileInfo['width'], fileInfo['height']))
        print("Video bitrate: %s bps, %s" %
              (fileInfo['videoBitrateb'], fileInfo['videoBitrate']))
        print("Framerate: %s fps" % fileInfo['frameRate'])
        print("Framecount: %s" % fileInfo['frameCount'])
        print("Format: %s" % fileInfo['videoFormat'])
        print("Codec ID: %s" % fileInfo['videoCodecID'])
        print("Pixel aspect ratio: %s" % fileInfo['pixelAspectRatio'])
        print("Display aspect ratio: %s, %s" %
              (fileInfo['displayAspectRatio'], fileInfo['displayAspectRatioTV']))
        print("Standard: %s" % fileInfo['tvStandard'])
        print("StreamSize: %s b, %s" %
              (fileInfo['videoStreamSizeb'], fileInfo['videoStreamSize']))
        print(error)

    ##### audio #####
    if verbose:
        print("----Gathering audio information...")

    cmd = "mediainfo %s '%s'" % (("--Inform=Audio;"
                                  "%Duration%,"
                                  "%Duration/String3%,"
                                  "%BitRate%,"
                                  "%BitRate/String%,"
                                  "%Format%,"
                                  "%CodecID%,"
                                  "%StreamSize%,"
                                  "%StreamSize/String%"),
                                 myFile)

    output, error = executeCmd(cmd, verbose)
    if output == None and error == None:
        if keepGoing:
            print("*** Execution took too long")
        else:
            onError(13, "Execution took too long")

    answer = output.replace("\n", "").split(',')

    infoNo = 0
    for key in ("audioDurations",
                "audioDuration",
                "audioBitrateb",
                "audioBitrate",
                "audioFormat",
                "audioCodecID",
                "audioStreamSizeb",
                "audioStreamSize"):
        try:
            fileInfo[key] = answer[infoNo]
        except:
            if not keepGoing:
                onError(15, "*** Could not get '%s'" % key)
            else:
                print("*** Could not get '%s'" % key)
            fileInfo[key] = "NA"
        infoNo += 1

    if info:
        print("Audio:")
        print("Duration: %s ms, %s" %
              (fileInfo['audioDurations'], fileInfo['audioDuration']))
        print("Audio bitrate: %s bps, %s" %
              (fileInfo['audioBitrateb'], fileInfo['audioBitrate']))
        print("Format: %s" % fileInfo['audioFormat'])
        print("Codec ID: %s" % fileInfo['audioCodecID'])
        print("Stream Size: %s b, %s" %
              (fileInfo['audioStreamSizeb'], fileInfo['audioStreamSize']))
        print(error)

    return fileInfo


def generateFrames(myFile, videoParams, sheetParams, tempDir, keepGoing, info, verbose):
    startOffset, endOffset, grabber, frameFormat = videoParams
    sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground, infoHeight = sheetParams

    fileInfo = {}

    newFileName = myFile.replace("'", "").replace("?", "")

    if myFile != newFileName:
        print("*** File name contains ' (single quote), Renaming...")
        print("--- Old name: %s" % myFile)
        print("--- New name: %s" % newFileName)
        os.rename(myFile, newFileName)
        myFile = newFileName

    fileInfo = getVideoInfo(myFile, fileInfo, info, keepGoing, verbose)

    try:
        videoDurations = int(fileInfo['videoDurations'])
    except:
        if not keepGoing:
            onError(
                14, "*** Could not set duration from video info\n    Setting duration from general info instead")
        else:
            print(
                "*** Could not set duration from video info\n    Setting duration from general info instead")
        videoDurations = int(fileInfo['generalDurations'])

    if startOffset + endOffset > videoDurations:  # too short video
        require = startOffset + endOffset + sheetColumns * sheetRows
        onError(9, "Video is too short, %s s, for your settings\nYour settings require at least %d s" % (
            videoDurations, require))

    interval = (videoDurations - startOffset - endOffset) / \
        (sheetColumns * sheetRows)  # how often to catch a frame
    if verbose:
        print("--- Will catch a frame every %s millisecond" % interval)

    fileName = fileInfo['fileName']
    if grabber == "mplayer":
        frameNames, grabTimes = mplayerGrabber(
            myFile, interval, fileName, videoParams, sheetParams, tempDir, keepGoing, verbose)

    return (frameNames, grabTimes, fileInfo)


def mplayerGrabber(myFile, interval, fileName, videoParams, sheetParams, tempDir, keepGoing, verbose):
    startOffset, endOffset, grabber, frameFormat = videoParams
    sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground, infoHeight = sheetParams

    frameNames = []
    grabTimes = []

    print("--- Grabbing frames with mplayer")

    for frameNo in range(0, sheetColumns * sheetRows):
        time = (startOffset + frameNo * interval) / 1000
        if verbose:
            print("--- Grabbing frame #%s at %s seconds" %
                  ((frameNo + 1), time))
        else:
            countDown = sheetColumns * sheetRows - frameNo
            progress = "%s " % countDown
            sys.stdout.write(progress)
            sys.stdout.flush()

        cmd = "/usr/bin/mplayer -nosound -ss %s -frames 1 -vo %s '%s'" % (
            time, frameFormat, myFile)

        output, error = executeCmd(cmd, verbose)
        if output == None and error == None:
            if keepGoing:
                print("*** Execution took too long")
            else:
                onError(13, "Execution took too long")

        if os.path.isfile("00000001.jpg"):
            if verbose:
                print("--- Moving frame #%s to temporary directory" %
                      (frameNo + 1))
            if frameNo + 1 < 10:
                frameCount = "0%d" % (frameNo + 1)
            else:
                frameCount = frameNo + 1

            frameName = "%s/%s.%s.%s" % (tempDir,
                                         fileName, frameCount, frameFormat)
            os.rename("00000001.jpg", frameName)
            frameNames.append(frameName)
            grabTimes.append(time)
        else:
            if keepGoing:
                print("\n*** Could not grab frame #%s. Skipping..." %
                      str(frameNo + 1))
            else:
                onError(10, "*** Could not create frame# %s" %
                        str(frameNo + 1))

    if not verbose:
        print()

    return (frameNames, grabTimes)
