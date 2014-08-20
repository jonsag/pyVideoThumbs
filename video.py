#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import os, shlex

from subprocess import call, check_output, Popen, PIPE

from error import *

def checkIfVideo(file, videoTypes, verbose):
    isVideo = False
    
    if verbose:
        print "--- Checking %s" % file

    extension = os.path.splitext(file)[1].lstrip('.')

    if extension in videoTypes:
        if os.path.isfile and not os.path.islink(file):
            if verbose:
                print "--- This is not a link and is a valid video file"
            print "\n%s\n------------------------------------------------------------------" % file
        isVideo = True

    return isVideo

def generateFrames(file, videoParams, sheetParams, tempDir, info, verbose):

    startOffset, endOffset, grabber, frameFormat = videoParams    
    sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground, infoHeight = sheetParams

    answer = []
    fileInfo = {}

    ##### general #####
    if verbose:
        print "--- Gathering general information..."

    cmd = "mediainfo %s '%s'" % ("--Inform=General;%Duration%,%Duration/String3%,%BitRate%,%BitRate/String%,%Format%,%FileSize%,%FileSize/String%,%StreamSize%,%StreamSize/String%,%FileName%,%FileExtension%", file)
    args = shlex.split(cmd)
    output, error = Popen(args, stdout = PIPE, stderr = PIPE).communicate()
    output = output.rstrip()
    answer = output.split(',')

    infoNo = 0
    for key in ("generalDurations", "generalDuration", "overallBitrates", "overallBitrate", "generalFormat", "fileSizeb", "fileSize", "generalStreamSizeb", "generalStreamSize", "fileName", "fileExtension"):
        fileInfo[key] = answer[infoNo]
        infoNo += 1
    
    if info:
        fullFileName = "%s.%s" % (fileInfo['fileName'], fileInfo['fileExtension'])

        print "General:"
        print "File name: %s" % fullFileName
        print "Duration: %s ms, %s" % (fileInfo['generalDurations'], fileInfo['generalDuration'])
        print "Overall bitrate: %s bps, %s" % (fileInfo['overallBitrates'], fileInfo['overallBitrate'])
        print "Format: %s" % fileInfo['generalFormat']
        print "File size: %s b, %s" % (fileInfo['fileSizeb'], fileInfo['fileSize'])
        print "Stream size: %s b, %s" % (fileInfo['generalStreamSizeb'], fileInfo['generalStreamSize'])
        print error


    ##### video #####
    if verbose:
        print "--- Gathering video information..."

    cmd = "mediainfo %s '%s'" % ("--Inform=Video;%Duration%,%Duration/String3%,%Width%,%Height%,%BitRate%,%BitRate/String%,%FrameRate%,%FrameCount%,%Format%,%CodecID%,%PixelAspectRatio%,%DisplayAspectRatio%,%DisplayAspectRatio/String%,%Standard%,%StreamSize%,%StreamSize/String%", file)
    args = shlex.split(cmd)
    output, error = Popen(args, stdout = PIPE, stderr = PIPE).communicate()
    output = output.rstrip()
    answer = output.split(',')

    infoNo = 0
    for key in ("videoDurations", "videoDuration", "width", "height", "videoBitrateb", "videoBitrate", "frameRate", "frameCount", "videoFormat", "videoCodecID", "pixelAspectRatio", "displayAspectRatio", "displayAspectRatioTV", "tvStandard", "videoStreamSizeb", "videoStreamSize"):
        fileInfo[key] = answer[infoNo]
        infoNo += 1

    if info:
        print "Video:"
        print "Duration: %s ms, %s" % (fileInfo['videoDurations'], fileInfo['videoDuration'])
        print "Width x height: %s x %s px" % (fileInfo['width'], fileInfo['height'])
        print "Video bitrate: %s bps, %s" % (fileInfo['videoBitrateb'], fileInfo['videoBitrate'])
        print "Framerate: %s fps" % fileInfo['frameRate']
        print "Framecount: %s" % fileInfo['frameCount']
        print "Format: %s" % fileInfo['videoFormat']
        print "Codec ID: %s" % fileInfo['videoCodecID']
        print "Pixel aspect ratio: %s" % fileInfo['pixelAspectRatio']
        print "Display aspect ratio: %s, %s" % (fileInfo['displayAspectRatio'], fileInfo['displayAspectRatioTV'])
        print "Standard: %s" % fileInfo['tvStandard']
        print "StreamSize: %s b, %s" % (fileInfo['videoStreamSizeb'], fileInfo['videoStreamSize'])
        print error

    ##### audio #####
    if verbose:
        print "--- Gathering audio information..."

    cmd = "mediainfo %s '%s'" % ("--Inform=Audio;%Duration%,%Duration/String3%,%BitRate%,%BitRate/String%,%Format%,%CodecID%,%StreamSize%,%StreamSize/String%", file)
    args = shlex.split(cmd)
    output, error = Popen(args, stdout = PIPE, stderr = PIPE).communicate()
    output = output.rstrip()
    answer = output.split(',')

    infoNo = 0
    for key in ("audioDurations", "audioDuration", "audioBitrateb", "audioBitrate", "audioFormat", "audioCodecID", "audioStreamSizeb", "audioStreamSize"):
        fileInfo[key] = answer[infoNo]
        infoNo += 1

    if info:
        print "Audio:"
        print "Duration: %s ms, %s" % (fileInfo['audioDurations'], fileInfo['audioDuration'])
        print "Audio bitrate: %s bps, %s" % (fileInfo['audioBitrateb'], fileInfo['audioBitrate'])
        print "Format: %s" % fileInfo['audioFormat']
        print "Codec ID: %s" % fileInfo['audioCodecID']
        print "Stream Size: %s b, %s" % (fileInfo['audioStreamSizeb'], fileInfo['audioStreamSize'])
        print error

    videoDurations = int(fileInfo['videoDurations'])

    if startOffset + endOffset > videoDurations: # too short video
        onError(9, videoDurations)

    interval = (videoDurations - startOffset - endOffset) / (sheetColumns * sheetRows) # how often to catch a frame                                                                 
    if verbose:
        print "--- Will catch a frame every %s millisecond" % interval

    fileName = fileInfo['fileName']
    if grabber == "mplayer":
        frameNames, grabTimes = mplayerGrabber(file, interval, fileName, videoParams, sheetParams, tempDir, verbose)

    return (frameNames, grabTimes, fileInfo)

def mplayerGrabber(file, interval, fileName, videoParams, sheetParams, tempDir, verbose):
    startOffset, endOffset, grabber, frameFormat = videoParams
    sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground, infoHeight = sheetParams

    frameNames = []
    grabTimes = []

    print "--- Grabbing frames with mplayer"

    # mplayer -nosound -ss $STEP -frames 1 -vo jpeg $FILE

    for frameNo in range (0, sheetColumns * sheetRows):
        time = (startOffset + frameNo * interval) / 1000
        if verbose:
            print "--- Grabbing frame #%s at %s seconds" % ((frameNo + 1), time)
        else:
            countDown = sheetColumns * sheetRows - frameNo
            progress = "%s " % countDown
            sys.stdout.write(progress)
            sys.stdout.flush()

        cmd = "/usr/bin/mplayer -nosound -ss %s -frames 1 -vo %s '%s'"  % (time, frameFormat, file) 
        args = shlex.split(cmd)
        output, error = Popen(args, stdout = PIPE, stderr = PIPE).communicate()

        #if error:
        #    print error

        if os.path.isfile("00000001.jpg"):
            if verbose:
                print "--- Moving frame #%s to temporary directory" % (frameNo + 1)
            if frameNo + 1< 10:
                frameCount = "0%d" % (frameNo +1)
            else:
                frameCount = frameNo + 1

            frameName = "%s/%s.%s.%s" % (tempDir, fileName, frameCount, frameFormat)
            os.rename("00000001.jpg", frameName)
            frameNames.append(frameName)
            grabTimes.append(time)
        else:
            onError(10, frameNo +1)

    if not verbose:
        print
            
    return (frameNames, grabTimes)
