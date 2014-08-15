#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

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