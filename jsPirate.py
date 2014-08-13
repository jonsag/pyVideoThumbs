#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import ConfigParser, os, getopt, sys, shlex

from subprocess import call, check_output, Popen, PIPE

config = ConfigParser.ConfigParser()
config.read("%s/config.ini" % os.path.dirname(os.path.realpath(__file__))) # read config file

sheetWidth = config.get('contactsheets','sheetWidth')
sheetHeight = config.get('contactsheets','sheetHeight')
sheetColumns = config.get('contactsheets','sheetColumns')
sheetRows = config.get('contactsheets','sheetRows')

############### functions ###############

def onError(errorCode, extra):
    print "\nError:"
    if errorCode == 1:
        print extra
        usage(errorCode)
    elif errorCode == 2:
        print "No options given"
        usage(errorCode)
    elif errorCode == 3:
        print "No program part chosen"
        usage(errorCode)
    elif errorCode == 4:
        print "File %s does not exist" % extra
        sys.exit(errorCode)
    elif errorCode == 5:
        print "%s is a link" % extra
        sys.exit(errorCode)
    elif errorCode == 6:
        print "%s is not a directory" % extra
        sys.exit(errorCode)
    elif errorCode == 7:
        print "You can't state both -f (--file) and -p (--path)"
        usage(errorCode)
    elif errorCode == 8:
        print "Last url did not have a following name"
        sys.exit(errorCode)
    elif errorCode == 9:
        print "First line was not a url"
        sys.exit(errorCode)

def usage(exitCode):
    print "\nUsage:"
    print "----------------------------------------"
    print "%s -f <file>" % sys.argv[0]
    print "    OR\n"
    print "%s -p <directory>" % sys.argv[0]

    sys.exit(exitCode)

############### handle arguments ###############
try:
    myopts, args = getopt.getopt(sys.argv[1:],'f:p:' , ['file=', 'path='])

except getopt.GetoptError as e:
    onError(1, str(e))

if len(sys.argv) == 1: # no options passed
    onError(2, 2)

file = ""
path = ""

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

if file and path:
    onError(7, 7)



############### functions ###############
def processFile(file):
    answer = []

    ##### general #####
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

    print "General:"
    print "File name: %s" % fullFileName
    print "Duration: %s s, %s" % (generalDurations, generalDuration)
    print "Overall bitrate: %s bps, %s" % (overallBitrates, overallBitrate)
    print "Format: %s" % generalFormat
    print "File size: %s b, %s" % (fileSizeb, fileSize)
    print "Stream size: %s b, %s" % (generalStreamSizeb, generalStreamSize)
    print error


    ##### video #####
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

    print "Video:"
    print "Duration: %s s, %s" % (videoDurations, VideoDuration)
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

    print "Audio:"
    print "Duration: %s s, %s" % (audioDurations, audioDuration)
    print "Audio bitrate: %s bps, %s" % (audioBitrateb, audioBitrate)
    print "Format: %s" % audioFormat
    print "Codec ID: %s" % audioCodecID
    print "Stream Size: %s b, %s" % (audioStreamSizeb, audioStreamSize)
    print error

############### single video file ###############
if file:
    print "%s\n------------------------------------------------------------------" % file
    processFile(file)
