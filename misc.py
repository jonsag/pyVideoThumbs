#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Encoding: UTF-8

import os

from error import *

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
                            dir = os.path.join(os.getcwd(), name)
                        else:
                            onError(12, path)
                            break
                    elif createDir.lower() == "n":
                        onError(7, os.path.join(os.getcwd(), name)) 
            else:
                os.makedirs(os.path.join(path, name))
                dir = os.path.join(path, name)
                break
        elif createOutDir.lower() == "n":
            onError(7, os.path.join(path, name))
    return dir
