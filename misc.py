#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import os, re, ConfigParser

from error import onError

config = ConfigParser.ConfigParser()  # define config file
config.read("%s/config.ini" % os.path.dirname(os.path.realpath(__file__)))  # read config file

videoTypes = (config.get('video', 'videoTypes')).split(',')  # allowed file types

sheetWidth = int(config.get('contactsheets', 'sheetWidth'))  # paramaters for the contact sheet
sheetHeight = int(config.get('contactsheets', 'sheetHeight'))
sheetColumns = int(config.get('contactsheets', 'sheetColumns'))
sheetRows = int(config.get('contactsheets', 'sheetRows'))
leftMargin = int(config.get('contactsheets', 'leftMargin'))
topMargin = int(config.get('contactsheets', 'topMargin'))
rightMargin = int(config.get('contactsheets', 'rightMargin'))
bottomMargin = int(config.get('contactsheets', 'bottomMargin'))
thumbPadding = int(config.get('contactsheets', 'thumbPadding'))
sheetBackground = config.get('contactsheets', 'sheetBackground')
infoHeight = int(config.get('contactsheets', 'infoHeight'))
sheetParams = [sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground, infoHeight]

startOffset = int(config.get('frameGrabbing', 'startOffset'))  # parameters for the frame grabs
endOffset = int(config.get('frameGrabbing', 'endOffset'))
grabber = config.get('frameGrabbing', 'grabber')
frameFormat = config.get('frameGrabbing', 'frameFormat')
videoParams = [startOffset, endOffset, grabber, frameFormat]

timeCode = config.get('timeCode', 'timeCode')
tcPlace = config.get('timeCode', 'tcPlace')
tcColour = config.get('timeCode', 'tcColour')
tcOutlineColour = config.get('timeCode', 'tcOutlineColour')
tcFont = config.get('timeCode', 'tcFont')
tcSize = int(config.get('timeCode', 'tcSize'))
tcParams = [timeCode, tcPlace, tcColour, tcOutlineColour, tcFont, tcSize]

infoColour = config.get('info', 'infoColour')
infoOutlineColour = config.get('info', 'infoOutlineColour')
infoFont = config.get('info', 'infoFont')
infoSize = int(config.get('info', 'infoSize'))
infoParams = [infoColour, infoOutlineColour, infoFont, infoSize]

tempDir = os.path.join(os.path.expanduser("~"), config.get('paths', 'tempDir'))  # temporary dir, used to store frame grabs


def makeDir(path, name):
    while True:
        createDir = raw_input('Do you want to create it? (Y/n)')
        if createDir.lower() == "y" or not createDir:
            if not os.access(path, os.W_OK):
                print "*** You do not have write access to %s" % path
                while True:
                    createDir = raw_input('Do you want to create it here instead? (Y/n)')
                    if createDir.lower() == "y" or not createDir:
                        if os.access(os.getcwd(), os.W_OK):
                            os.makedirs(os.path.join(os.getcwd(), name))
                            dirName = os.path.join(os.getcwd(), name)
                        else:
                            onError(12, "No write access at %s either" % path)
                            break
                    elif createDir.lower() == "n":
                        onError(7, "Opted not to create directory %s" % os.path.join(os.getcwd(), name)) 
            else:
                os.makedirs(os.path.join(path, name))
                dirName = os.path.join(path, name)
                break
        elif createDir.lower() == "n":
            onError(7, "Opted not to create directory %s" % os.path.join(path, name))
    return dirName

def checkFileName(myFile, keepGoing, noRename, outDir, verbose):
    number = 0
    if verbose:
        print "--- Checking if file name complies..."
    
    path =  os.path.dirname(myFile)   
    fileName, suffix =  os.path.splitext(os.path.basename(myFile))
    
    #allowedCharsString = '[^A-Za-z0-9()_- åäöÅÄÖ]+'
    allowedCharsString = '[^A-Za-z0-9()_]+'
      
    if fileName != re.sub(allowedCharsString, '_', fileName):
        if noRename:
            print "*** Filename does not comply to our rules,\n    but renaming has been disabled"
        else:
            print "*** %s does not comply to our file naming standard\n    Will rename..." % fileName
            print "--- New file name will be: %s" % re.sub(allowedCharsString, '_', fileName)
            newName = re.sub('[^A-Za-z0-9]+', '_', fileName)
            print os.path.join(path, "%s%s" % (newName, suffix))
    
            if os.path.isfile(os.path.join(path, 
                                           "%s%s" % (newName, suffix))
                                           ):
                print "*** %s already exists" % os.path.join(path, "%s%s" % (newName, suffix))
                while True:
                    number += 1
                    print ("--- Renaming it to %s" % 
                           os.path.join(path, "%s_%s%s" % (newName, number, suffix))
                           )
                    if os.path.isfile(os.path.join(path, 
                                                   "%s_%s%s" % (newName, number, suffix))
                                                   ):
                        print("*** %s already exists" % 
                              os.path.join(path, 
                                           "%s_%s%s" % (newName, number, suffix))
                                           )
                    else:
                        os.rename( (os.path.join(path, "%s%s" % (fileName, suffix))), 
                                   (os.path.join(path, "%s_%s%s" % (newName, number, suffix)))
                                   )   
                        myFile = os.path.join(path, "%s_%s%s" % (newName, number, suffix))
                        break
            else:
                os.rename( (os.path.join(path, "%s%s" % (fileName, suffix))), 
                           (os.path.join(path, "%s%s" % (newName, suffix)))
                           )
                myFile = os.path.join(path, "%s%s" % (newName, suffix))
        
    return myFile

def contactSheetExist(path, myFile, outDir, verbose):
    sheetName = os.path.join(path, outDir, "%s.png" % myFile)
    
    if os.path.isfile(sheetName):
        if verbose:
            print "--- %s already exist" % sheetName
        exists = True
    else:
        if verbose:
            print "--- %s does not exist" % sheetName
        exists = False
        
    return exists
    
    
    
    
    
