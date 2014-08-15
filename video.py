#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import os, shlex

from subprocess import call, check_output, Popen, PIPE

from error import *

def generateFrames(file, videoParams, sheetParams, tempDir, info, verbose):

    startOffset, endOffset, grabber, frameFormat = videoParams    
    sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground = sheetParams

    answer = []

    ##### general #####
    if verbose:
        print "--- Gathering general information..."

    cmd = "mediainfo %s '%s'" % ("--Inform=General;%Duration%,%Duration/String3%,%BitRate%,%BitRate/String%,%Format%,%FileSize%,%FileSize/String%,%StreamSize%,%StreamSize/String%,%FileName%,%FileExtension%", file)
    args = shlex.split(cmd)
    output, error = Popen(args, stdout = PIPE, stderr = PIPE).communicate()
    output = output.rstrip()
    answer = output.split(',')

    generalDurations = int(answer[0])
    generalDuration = answer[1]
    overallBitrates = int(answer[2])
    overallBitrate = answer[3]
    generalFormat = answer[4]
    fileSizeb = int(answer[5])
    fileSize = answer[6]
    generalStreamSizeb = answer[7]
    generalStreamSize = answer[8]
    fileName = answer[9]
    fileExtension = answer[10]
    fullFileName = "%s.%s" % (fileName, fileExtension)
        
    if info:
        print "General:"
        print "File name: %s" % fullFileName
        print "Duration: %s ms, %s" % (generalDurations, generalDuration)
        print "Overall bitrate: %s bps, %s" % (overallBitrates, overallBitrate)
        print "Format: %s" % generalFormat
        print "File size: %s b, %s" % (fileSizeb, fileSize)
        print "Stream size: %s b, %s" % (generalStreamSizeb, generalStreamSize)
        print error


    ##### video #####
    if verbose:
        print "--- Gathering video information..."

    cmd = "mediainfo %s '%s'" % ("--Inform=Video;%Duration%,%Duration/String3%,%Width%,%Height%,%BitRate%,%BitRate/String%,%FrameRate%,%FrameCount%,%Format%,%CodecID%,%PixelAspectRatio%,%DisplayAspectRatio%,%DisplayAspectRatio/String%,%Standard%,%StreamSize%,%StreamSize/String%", file)
    args = shlex.split(cmd)
    output, error = Popen(args, stdout = PIPE, stderr = PIPE).communicate()
    output = output.rstrip()
    answer = output.split(',')

    videoDurations = int(answer[0])
    VideoDuration = answer[1]
    width = int(answer[2])
    height = int(answer[3])
    videoBitrateb = int(answer[4])
    videoBitrate = answer[5]
    frameRate = answer[6]
    frameCount = int(answer[7])
    videoFormat = answer[8]
    videoCodecID = answer[9]
    pixelAspectRatio = answer[10]
    displayAspectRatio = answer[11]
    displayAspectRatioTV = answer[12]
    tvStandard = answer[13]
    videoStreamSizeb = answer[14]
    videoStreamSize = answer[15]

    if info:
        print "Video:"
        print "Duration: %s ms, %s" % (videoDurations, VideoDuration)
        print "Width x height: %s x %s px" % (width, height)
        print "Video bitrate: %s bps, %s" % (videoBitrateb, videoBitrate)
        print "Framerate: %s fps" % frameRate
        print "Framecount: %s" % frameCount
        print "Format: %s" % videoFormat
        print "Codec ID: %s" % videoCodecID
        print "Pixel aspect ratio: %s" % pixelAspectRatio
        print "Display aspect ratio: %s, %s" % (displayAspectRatio, displayAspectRatioTV)
        print "Standard: %s" % tvStandard
        print "StreamSize: %s b, %s" % (videoStreamSizeb, videoStreamSize)
        print error

    ##### audio #####
    if verbose:
        print "--- Gathering audio information..."

    cmd = "mediainfo %s '%s'" % ("--Inform=Audio;%Duration%,%Duration/String3%,%BitRate%,%BitRate/String%,%Format%,%CodecID%,%StreamSize%,%StreamSize/String%", file)
    args = shlex.split(cmd)
    output, error = Popen(args, stdout = PIPE, stderr = PIPE).communicate()
    output = output.rstrip()
    answer = output.split(',')

    audioDurations = int(answer[0])
    audioDuration = answer[1]
    audioBitrateb = int(answer[2])
    audioBitrate = answer[3]
    audioFormat = answer[4]
    audioCodecID = answer[5]
    audioStreamSizeb = answer[6]
    audioStreamSize = answer[7]

    if info:
        print "Audio:"
        print "Duration: %s ms, %s" % (audioDurations, audioDuration)
        print "Audio bitrate: %s bps, %s" % (audioBitrateb, audioBitrate)
        print "Format: %s" % audioFormat
        print "Codec ID: %s" % audioCodecID
        print "Stream Size: %s b, %s" % (audioStreamSizeb, audioStreamSize)
        print error

    if startOffset + endOffset > videoDurations: # too short video
        onError(9, videoDurations)

    interval = (videoDurations - startOffset - endOffset) / (sheetColumns * sheetRows) # how often to catch a frame                                                                 
    if verbose:
        print "--- Will catch a frame every %s millisecond" % interval

    if grabber == "mplayer":
        frameNames = mplayerGrabber(file, interval, fileName, videoParams, sheetParams, tempDir, verbose)

    return frameNames

def mplayerGrabber(file, interval, fileName, videoParams, sheetParams, tempDir, verbose):
    startOffset, endOffset, grabber, frameFormat = videoParams
    sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground = sheetParams

    frameNames = []

    print "--- Grabbing frames with mplayer"

    # mplayer -nosound -ss $STEP -frames 1 -vo jpeg $FILE

    for frameNo in range (0, sheetColumns * sheetRows):
        time = (startOffset + frameNo * interval) / 1000
        if verbose:
            print "--- Grabbing frame# %s at %s seconds" % ((frameNo + 1), time)

        cmd = "/usr/bin/mplayer -nosound -ss %s -frames 1 -vo %s '%s'"  % (time, frameFormat, file) 
        args = shlex.split(cmd)
        output, error = Popen(args, stdout = PIPE, stderr = PIPE).communicate()

        #if error:
        #    print error

        if os.path.isfile("00000001.jpg"):
            if verbose:
                print "--- Moving frame# %s to temporary directory" % (frameNo + 1)
            if frameNo + 1< 10:
                frameCount = "0%d" % (frameNo +1)
            else:
                frameCount = frameNo + 1

            frameName = "%s/%s.%s.%s" % (tempDir, fileName, frameCount, frameFormat)
            os.rename("00000001.jpg", frameName)
            frameNames.append(frameName)
        else:
            onError(10, frameNo +1)
            
    return frameNames
