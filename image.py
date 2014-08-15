#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

from PIL import Image

def makeContactSheet(frameNames, sheetParams, verbose):
    sheetWidth, sheetHeight, sheetColumns, sheetRows, leftMargin, topMargin, rightMargin, bottomMargin, thumbPadding, sheetBackground = sheetParams

    sampleFrame = Image.open(frameNames[0])
    thumbWidth, thumbHeight = sampleFrame.size
    Image.close()

    if verbose:
        print "--- Thumbs width x height: %s x %s" % (thumbWidth, thumbHeight)

    thumbs = [Image.open(frame).resize((thumbWidth, thumbHeight)) for frame in frameNames] # Read in all images and resize appropriately

    marginsWidth = leftMargin + rightMargin # Calculate the size of the output image, based on the photo thumb sizes, margins, and padding
    marginsHeight = topMargin + bottomMargin

    paddingsWidth = (sheetColumns - 1) * thumbPadding
    paddingsHeight = (sheetRows - 1) * thumbPadding
    contactSheetSize = (sheetColumns * thumbWidth + marginsWidth + paddingsWidth, sheetRows * thumbHeight + marginsHeight + paddingsHeight)

    contactSheet = Image.new('RGB', contactSheetSize, "rgb%s" % sheetBackground) # Create the new image

    # Insert each thumb:
    for rowNo in range(sheetRows):
        for columnNo in range(sheetColumns):
            left = leftMargin + columnNo * (thumbWidth + thumbPadding)
            right = left + thumbWidth
            upper = topMargin + rowNo * (thumbHeight + thumbPadding)
            lower = upper + thumbHeight
            bbox = (left, upper, right, lower)
            try:
                image = thumbs.pop(0)
            except:
                break
            contactSheet.paste(image, bbox)
    return contactSheet
