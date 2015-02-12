#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import sys

def onError(errorCode, extra):
    print "\nError:"
    if errorCode in(1, 2):
        print extra
        usage(errorCode)
    elif errorCode in (4, 5, 6 ,7 ,8, 11, 12):
        print extra
        sys.exit(errorCode)
    elif errorCode in (9, 10, 11, 12):
        print extra
        raw_input('Press [Return] key to continue')

def usage(exitCode):
    print "\nUsage:"
    print "----------------------------------------"
    print "%s -f <file> [-o <directory>] [-i -k -v]" % sys.argv[0]
    print "  Creates a single contact sheet for <file> [and puts it in <directory> ]"
    print 
    print "%s -p <in directory> [-o <out directory>][-i -k -v]" % sys.argv[0]
    print "  Scans <in directory> for video files, creates contact sheets from them [and puts them in <outdirectory>]"
    print
    print "    Otions:"
    print "    -i display file 'i'nfo"
    print "    -k 'k'eep going on errors"
    print "    -v 'v'erbose output"
    print
    print "%s -h" % sys.argv[0]
    print "  Prints this"
    
    sys.exit(exitCode)
