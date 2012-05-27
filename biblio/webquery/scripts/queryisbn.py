#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Retreive bibliographic information for a given ISBN.

"""
# TODO: throttle parameter?
# TODO: Amazon query?
# TODO: output in other formats?

__docformat__ = 'restructuredtext en'


### IMPORTS ###

import sys
from os import path
from optparse import OptionParser
from exceptions import BaseException

from config import *
from common import *


### CONSTANTS & DEFINES ###

PRINT_FIELDS = [
	'title', 
	'authors',
	'publisher',
	'year',
	'lang',
]

_DEV_MODE = False

### IMPLEMENTATION ###

def parse_args():
	# Construct the option parser.
	usage = '%prog [options] ISBNs ...'
	version = "version %s" %  script_version
	epilog=''
	description = 'Return bibliographic information from webservices for ' \
		'supplied ISBNs.'
	optparser = OptionParser (usage=usage, version=version,
		description=description, epilog=epilog)
	add_shared_options (optparser)

	# parse and check args
	options, isbns = optparser.parse_args()
	
	if (not isbns):
		optparser.error ('No ISBNs specified')
	check_shared_options (options, optparser)
	
	## Postconditions & return:
	return isbns, options


def main():
	isbn_list, options = parse_args()
	webqry = construct_webquery (options.webservice, options.service_key)
	try:
		for isbn in isbn_list:
			print '%s:' % isbn
			rec_list = webqry.query_bibdata_by_isbn (isbn, format='bibrecord')
			if (rec_list):
				for f in PRINT_FIELDS:
					if (getattr (rec_list[0], f)):
						print '   %s: %s' % (f, getattr (rec_list[0], f))
			else:
				print '   No results'
	except BaseException, err:
		if (_DEV_MODE or options.debug):
			raise
		else:
			sys.exit (err)
	except:
		if (_DEV_MODE or option.debug):
			raise
		else:
			sys.exit ("An unknown error occurred.")
	
	
### TEST & DEBUG ###

### MAIN ###

if __name__ == '__main__':
	main()
	

### END ######################################################################
