#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

#from pyVideoThumbs import startOffset, endOffset, sheetColumns, sheetRows

import sys

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
        print "Opted not to create directory %s" % extra
        sys.exit(errorCode)
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
    elif errorCode == 11:
        print "*** %s is not a valid directory" % extra
        usage(errorCode)
    elif errorCode == 12:
        print "No write access at %s either" % extra
        sys.exit(errorCode)

def usage(exitCode):
    print "\nUsage:"
    print "----------------------------------------"
    print "%s -f <file> [-o <directory>] [-i]" % sys.argv[0]
    print "  Creates a single contact sheet for <file> [and puts it in <directory> ]"
    print "    Options: -i if you want to display file 'i'nfo"
    print 
    print "%s -p <in directory> [-o <out directory>][-i]" % sys.argv[0]
    print "  Scans <in directory> for video files, creates contact sheets from them [and puts them in <outdirectory>]"
    print "  Options: -i if you want to display file 'i'nfo"

    sys.exit(exitCode)
