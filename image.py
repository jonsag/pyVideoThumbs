#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import os, datetime

from PIL import Image, ImageChops, ImageFont, ImageDraw

from decimal import Decimal, getcontext

from datetime import timedelta

getcontext().prec = 3 # precision of floating point

def makeContactSheet(frameNames, grabTimes, sheetParams, tcParams, tempDir, verbose):
    sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground, infoHeight = sheetParams
    trimmedFrames = []
    frameNo = 0

    if verbose:
        originalFrame = Image.open(frameNames[0])
        originalWidth, originalHeight = originalFrame.size
        print "--- Original width x height: %s x %s px" % (originalWidth, originalHeight)

    print "--- Trimming frames"

    for frame in frameNames:
        frameNo += 1
        trimmedFileName = "%s/%s.trimmed.png" % (tempDir, os.path.splitext(os.path.basename(frame))[0])
        if verbose:
            print "--- Removing borders from frame #%s" % frameNo
        image = Image.open(frame)
        trimmedFrame = removeBorders(image, verbose)        
        trimmedFrame.save(trimmedFileName)
        trimmedFrames.append(trimmedFileName)

    if verbose:
        print "--- Calculating thumb size"

    trimmedFrame = Image.open(trimmedFrames[0])
    trimmedWidth, trimmedHeight = trimmedFrame.size
    trimmedWidth = Decimal(trimmedWidth)
    trimmedHeight = Decimal(trimmedHeight)

    trimmedRatio = trimmedWidth / trimmedHeight

    if trimmedWidth >= trimmedHeight:
        thumbWidth = (sheetWidth - leftMargin - rightMargin - (sheetColumns -1) * thumbPadding) / sheetColumns
        thumbHeight = thumbWidth / trimmedRatio
    else:
        thumbHeight = (sheetHeight - topMargin - bottomMargin - (sheetRows -1) * thumbPadding) / sheetRows
        thumbWidth = thumbHeight * trimmedRatio

    sheetW = leftMargin + rightMargin + (sheetColumns - 1) * thumbPadding + thumbWidth * sheetColumns
    sheetH = topMargin + bottomMargin + (sheetRows - 1) * thumbPadding + thumbHeight * sheetRows

    if verbose:
        print "--- Trimmed width x height: %s x %s px" % (trimmedWidth, trimmedHeight)
        print "--- Trimmed ratio: %s" % trimmedRatio
        print "--- Thumbs will be width x height: %s x %s px" % (thumbWidth, thumbHeight)
        print "--- Contactsheet will be width x height: %s x %s px" % (sheetW, sheetH)
        
    print "--- Creating thumbs"
    thumbFrames = makeThumbs(trimmedFrames, tcParams, grabTimes, thumbWidth, thumbHeight, tempDir, verbose)

    thumbs = [Image.open(frame).resize((thumbWidth, thumbHeight)) for frame in thumbFrames] # Read in all images and resize appropriately

    marginsWidth = leftMargin + rightMargin # Calculate the size of the output image, based on the photo thumb sizes, margins, and padding
    marginsHeight = topMargin + bottomMargin

    paddingsWidth = (sheetColumns - 1) * thumbPadding
    paddingsHeight = (sheetRows - 1) * thumbPadding + infoHeight
    contactSheetSize = (sheetColumns * thumbWidth + marginsWidth + paddingsWidth, sheetRows * thumbHeight + marginsHeight + paddingsHeight)

    print "--- Creating contactsheet"
    contactSheet = Image.new('RGB', contactSheetSize, sheetBackground) # create the new image

    for rowNo in range(sheetRows): # insert thumbs into contact sheet
        for columnNo in range(sheetColumns):
            left = leftMargin + columnNo * (thumbWidth + thumbPadding)
            right = left + thumbWidth
            upper = topMargin + rowNo * (thumbHeight + thumbPadding) + infoHeight
            lower = upper + thumbHeight
            bbox = (left, upper, right, lower)
            try:
                image = thumbs.pop(0)
            except:
                break
            contactSheet.paste(image, bbox)
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

    for frame in trimmedFrames:
        frameNo += 1
        thumbFileName = "%s/%s.thumb.png" % (tempDir, os.path.splitext(os.path.basename(frame))[0])
        if verbose:
            print "--- Creating thumb #%s" % frameNo
        thumb = Image.open(frame) # open screen shot
        thumb.thumbnail(size, Image.ANTIALIAS) # resize to thumb size

        if timeCode: # if time code should be added to thumb
            if verbose:
                print "--- Inserting time code %s" % grabTime

            grabTime = str(timedelta(seconds=grabTimes[frameNo - 1])) # time when screen shot was taken
            if tcPlace == "tl":
                tcX = 10
                tcY = 10
            elif tcPlace == "bl":
                tcX = 10
                tcY = thumbHeight - 10 - tcSize

            draw = ImageDraw.Draw(thumb)
            font = ImageFont.truetype(tcFont, tcSize)
            draw.text((tcX + 1, tcY), grabTime, tcOutlineColour, font=font) # drawing the outline colour
            draw.text((tcX - 1, tcY), grabTime, tcOutlineColour, font=font)
            draw.text((tcX, tcY - 1), grabTime, tcOutlineColour, font=font)
            draw.text((tcX, tcY + 1), grabTime, tcOutlineColour, font=font)
            draw.text((tcX, tcY), grabTime, tcColour, font=font) # drawing with the fill colour

        thumb.save(thumbFileName)
        thumbFrames.append(thumbFileName)

    return thumbFrames
