#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Constants and definitions for scripts.

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

from biblio.webquery.xisbn import XisbnQuery
from biblio.webquery.loc import LocQuery
from biblio.webquery.isbndb import IsbndbQuery

try:
	from biblio.webquery import __version__
except:
	__version__ = 'unknown'

__all__ = [
	'WEBSERVICES',
	'WEBSERVICE_LOOKUP',
	'DEFAULT_WEBSERVICE',
]
	

### CONSTANTS & DEFINES ###

WEBSERVICES = [
	{
		'id':      'xisbn', 
		'title':   'WorldCat xISBN',
		'ctor':    XisbnQuery,
	},
	{
		'id':      'isbndb', 
		'title':   'ISBNdb',
		'ctor':    IsbndbQuery,
	},
#	{
#		'id':      'loc', 
#		'title':   'Library of Congress',
#		'ctor':    LocQuery,
#	},
]
DEFAULT_WEBSERVICE = WEBSERVICES[0]
WEBSERVICE_LOOKUP = dict ([(s['id'], s) for s in WEBSERVICES])


### IMPLEMENTATION ###

### TEST & DEBUG ###

### MAIN ###

### END ######################################################################
