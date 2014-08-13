#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import ConfigParser, os, getopt, sys, shlex

from subprocess import call, check_output, Popen, PIPE

config = ConfigParser.ConfigParser()
config.read("%s/config.ini" % os.path.dirname(os.path.realpath(__file__))) # read config file

sheetWidth = int(config.get('contactsheets', 'sheetWidth'))
sheetHeight = int(config.get('contactsheets', 'sheetHeight'))
sheetColumns = int(config.get('contactsheets', 'sheetColumns'))
sheetRows = int(config.get('contactsheets', 'sheetRows'))
horizontalSpacing = int(config.get('contactsheets', 'horizontalSpacing'))
verticalSpacing = int(config.get('contactsheets', 'verticalSpacing'))

startOffset = int(config.get('frameGrabbing', 'startOffset'))
endOffset = int(config.get('frameGrabbing', 'endOffset'))
grabber = config.get('frameGrabbing', 'grabber')
frameFormat = config.get('frameGrabbing', 'frameFormat')

tempDir = os.path.join(os.path.expanduser("~"), config.get('paths','tempDir'))

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
        print "Opted not to create temporary directory %s" % extra
        sys.exit(7)
    elif errorCode == 8:
        print "Temporary directory %s not writeable" % extra
        sys.exit(errorCode)
    elif errorCode == 9:
        print "Video is too short, %s s, for your settings" % extra
        require = startOffset + endOffset + sheetColumns * sheetRows
        print "Your settings require at least %d s" % require
        raw_input('Press [Return] key to continue')
    elif errorCode == 10:
        print "*** Could not create frame# %s" % extra
        raw_input('Press [Return] key to continue')

def usage(exitCode):
    print "\nUsage:"
    print "----------------------------------------"
    print "%s -f <file> [-i]" % sys.argv[0]
    print "  Options: -i if you want to display file 'i'nfo"
    print "    OR\n"
    print "%s -p <directory> [-i]" % sys.argv[0]
    print "  Options: -i if you want to display file 'i'nfo"

    sys.exit(exitCode)

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

############### more functions ###############
def processFile(file):
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

    interval = calculate(videoDurations)
    
    if grabber == "mplayer":
        mplayerGrabber(interval, fileName)

def calculate(videoDurations):
    if startOffset + endOffset > videoDurations:
        onError(9, videoDurations)

    interval = (videoDurations - startOffset - endOffset) / (sheetColumns * sheetRows)
    if verbose:
        print "--- Will catch a frame every %s millisecond" % interval

    return interval

def mplayerGrabber(interval, fileName):
    print "--- Grabbing frames with mplayer"

    # mplayer -nosound -ss $STEP -frames 1 -vo jpeg $FILE

    for frameNo in range (0, sheetColumns * sheetRows):
        time = startOffset + frameNo * interval
        if verbose:
            print "--- Grabbing frame# %s at %s seconds" % ((frameNo + 1), time)

        cmd = "/usr/bin/mplayer -nosound -ss %s -frames 1 -vo %s '%s'"  % (time, frameFormat, file) 
        args = shlex.split(cmd)
        output, error = Popen(args, stdout = PIPE, stderr = PIPE).communicate()

        "print output"
        #if error:
        #    print error

        if os.path.isfile("00000001.jpg"):
            if verbose:
                print "--- Moving frame# %s to temporary directory" % (frameNo + 1)
            if frameNo + 1< 10:
                frameCount = "0%d" % (frameNo +1)
            else:
                frameCount = frameNo + 1
            os.rename("00000001.jpg", "%s/%s.%s.%s" % (tempDir, fileName, frameCount, frameFormat))
        else:
            onError(10, frameNo +1)
############### single video file ###############
if file:
    print "\n%s\n------------------------------------------------------------------" % file
    processFile(file)
