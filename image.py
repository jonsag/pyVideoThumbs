#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import os, datetime, sys

from PIL import Image, ImageChops, ImageFont, ImageDraw

from decimal import Decimal, getcontext

from datetime import timedelta

getcontext().prec = 5 # precision of floating point

def makeContactSheet(frameNames, grabTimes, fileInfo, sheetParams, tcParams, infoParams, tempDir, info, verbose):
    sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground, infoHeight = sheetParams

    trimmedFrames = []
    frameNo = 0

    infoHeight = sheetWidth * infoHeight / 100

    print "--- Trimming borders"
    noFrames = len(frameNames)
    for frame in frameNames: # removing borders from screen shots
        frameNo += 1
        if verbose:
            print "--- Removing borders from frame #%s" % frameNo
        else:
            countDown = noFrames - frameNo + 1
            progress = "%s " % countDown
            sys.stdout.write(progress)
            sys.stdout.flush()
        image = Image.open(frame)
        trimmedFrame = removeBorders(image, verbose)
        if verbose:
            trWidth, trHeight = trimmedFrame.size
            print "--- Trimmed size width x height: %s x %s px" % (trWidth, trHeight)
        trimmedFileName = "%s/%s.trimmed.png" % (tempDir, os.path.splitext(os.path.basename(frame))[0])
        trimmedFrame.save(trimmedFileName)
        trimmedFrames.append(trimmedFileName)

    if not verbose:
        print
    else:
        print "--- Calculating thumb size"

    trimmedFrame = Image.open(trimmedFrames[0])
    trimmedWidth, trimmedHeight = trimmedFrame.size
    trimmedWidth = Decimal(trimmedWidth)
    trimmedHeight = Decimal(trimmedHeight)
    trimmedRatio = trimmedWidth / trimmedHeight

    thumbWidth = (sheetWidth - leftMargin - rightMargin - (sheetColumns -1) * thumbPadding) / sheetColumns
    thumbHeight = int(thumbWidth / trimmedRatio)
    
    if info or verbose:
        print "--- Trimmed width x height: %s x %s px" % (trimmedWidth, trimmedHeight)
        print "--- Trimmed ratio: %s" % trimmedRatio
        print "--- Thumbs will be width x height: %s x %s px" % (thumbWidth, thumbHeight)
        
    print "--- Creating thumbs"
    thumbs = makeThumbs(trimmedFrames, tcParams, grabTimes, thumbWidth, thumbHeight, tempDir, verbose) # create thumbs from screen shots
    thumbs = [Image.open(frame).resize((thumbWidth, thumbHeight)) for frame in thumbs] # read in all images and resize appropriately

    marginsWidth = leftMargin + rightMargin # calculate the size of the output image, based on the photo thumb sizes, margins, and padding
    marginsHeight = topMargin + bottomMargin

    paddingsWidth = (sheetColumns - 1) * thumbPadding
    paddingsHeight = (sheetRows - 1) * thumbPadding + infoHeight
    #sheetWidth = int(float(sheetColumns * thumbWidth + marginsWidth + paddingsWidth))
    #sheetHeight = int(float(sheetRows * thumbHeight + marginsHeight + paddingsHeight))
    sheetWidth = sheetColumns * thumbWidth + marginsWidth + paddingsWidth
    sheetHeight = sheetRows * thumbHeight + marginsHeight + paddingsHeight

    contactSheetSize = (sheetWidth, sheetHeight)

    print "--- Creating contactsheet"
    contactSheet = Image.new('RGB', contactSheetSize, sheetBackground) # create the new image
    
    if info or verbose:
        print "--- Contact sheet is width x height: %s x %s px" % (sheetWidth, sheetHeight)

    thumbNo = 0
    if not verbose:
        print "--- Inserting thumbs"

    for rowNo in range(sheetRows): # insert thumbs into contact sheet
        for columnNo in range(sheetColumns):
            left = leftMargin + columnNo * (thumbWidth + thumbPadding) # left X coordinate                                                                             
            upper = infoHeight + topMargin + rowNo * (thumbHeight + thumbPadding) # left Y coordinate
            right = left + thumbWidth # right X coordinate
            lower = upper + thumbHeight # right Y coordinate
            bbox = (left, upper, right, lower)
            try:
                image = thumbs.pop(0)
            except:
                break
            thumbNo += 1
            if verbose:
                print "--- Inserting thumb #%s at %s, %s, %s, %s. Gives a thumb size of %s x %s px" % (thumbNo, left, upper, right, lower, right - left, lower - upper)
            else:
                countDown = noFrames - thumbNo + 1
                progress = "%s " % countDown
                sys.stdout.write(progress)
                sys.stdout.flush()
            try:
                contactSheet.paste(image, bbox)
            except:
                print "Unexpected error:", sys.exc_info()[0]
                if not verbose:
                    print
                print "*** Error inserting thumb #%s" % thumbNo
                break

    if not verbose:
        print

    contactSheet = addInfo(contactSheet, infoParams, fileInfo, infoHeight, verbose)

    return contactSheet

def removeBorders(file, verbose):
    background = Image.new(file.mode, file.size, file.getpixel((0,0))) # create a new image with the same colour as pixel at 0, 0
    diff = ImageChops.difference(file, background) # the absolute value of the difference between the original image and the new image
    diff = ImageChops.add(diff, diff, 0.1, -100)
    bbox = diff.getbbox()
    if bbox:
        return file.crop(bbox)

def makeThumbs(trimmedFrames, tcParams, grabTimes, thumbWidth, thumbHeight, tempDir, verbose):
    timeCode, tcPlace, tcColour, tcOutlineColour, tcFont, tcSize = tcParams

    frameNo = 0
    thumbFrames = []

    size = thumbWidth, thumbHeight
    tcSize = thumbHeight * tcSize / 100

    noFrames = len(trimmedFrames)
    for frame in trimmedFrames:
        frameNo += 1
        thumbFileName = "%s/%s.thumb.png" % (tempDir, os.path.splitext(os.path.basename(frame))[0])
        if verbose:
            print "--- Creating thumb #%s to width x height: %s x %s px" % (frameNo, thumbWidth, thumbHeight)
        else:
            countDown = noFrames - frameNo + 1
            progress = "%s " % countDown
            sys.stdout.write(progress)
            sys.stdout.flush()
        thumb = Image.open(frame) # open screen shot
        thumb.thumbnail(size, Image.ANTIALIAS) # resize to thumb size
        if verbose:
            thWidth, thHeight = thumb.size
            print "--- New size width x height: %s x %s px" % (thWidth, thHeight)

        if timeCode: # if time code should be added to thumb
            grabTime = str(timedelta(seconds=grabTimes[frameNo - 1])) # time when screen shot was taken

            if verbose:
                print "--- Inserting time code %s" % grabTime

            if tcPlace == "tl":
                tcX = 10
                tcY = 10
            elif tcPlace == "bl":
                tcX = 10
                tcY = thumbHeight - 10 - tcSize

            thumb = printTextOutline(thumb, tcX, tcY, grabTime, tcOutlineColour, tcFont, tcSize) # print text outline
            draw = ImageDraw.Draw(thumb)
            font = ImageFont.truetype(tcFont, tcSize)
            draw.text((tcX, tcY), grabTime, tcColour, font=font) # drawing with the fill colour

        thumb.save(thumbFileName)
        thumbFrames.append(thumbFileName)

    if not verbose:
        print

    return thumbFrames

def printTextOutline(image, posX, posY, text, outlineColour, font, fontSize):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font, fontSize)
    draw.text((posX + 1, posY), text, outlineColour, font=font) # drawing the outline colour                                                                            
    draw.text((posX - 1, posY), text, outlineColour, font=font)
    draw.text((posX, posY - 1), text, outlineColour, font=font)
    draw.text((posX, posY + 1), text, outlineColour, font=font)
    return image

def addInfo(contactSheet, infoParams, fileInfo, infoHeight, verbose):
    infoColour, infoOutlineColour, infoFont, infoSize = infoParams

    posX = 2
    posY = 2
    paddingY = 2
    rows = 4

    infoSize = (infoHeight - (rows - 1) * paddingY - posX * 2) / rows

    print "--- Adding video information"
    draw = ImageDraw.Draw(contactSheet)
    font = ImageFont.truetype(infoFont, infoSize)
    draw.text((posX, posY), "File name: %s.%s" % (fileInfo['fileName'], fileInfo['fileExtension']), infoColour, font=font)
    draw.text((posX, posY + infoSize + paddingY), "Duration: %s" % fileInfo['generalDuration'], infoColour, font=font)
    draw.text((posX, posY + infoSize * 2 + paddingY * 2), "File size: %s" % fileInfo['fileSize'], infoColour, font=font)
    draw.text((posX, posY + infoSize * 3 + paddingY * 3), "Width x height: %s x %s px" % (fileInfo['width'], fileInfo['height']), infoColour, font=font)
    return contactSheet
