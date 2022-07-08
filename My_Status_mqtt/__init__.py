#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running
