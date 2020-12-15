#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# Author:曹敬贺


class JDException(Exception):

    def __init__(self, message):
        super().__init__(message)
        print("%s" % message)