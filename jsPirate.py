#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import ConfigParser, os, getopt, sys

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
