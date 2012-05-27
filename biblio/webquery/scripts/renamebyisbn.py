#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rename files as by the ISBN buried in their original name.

"""
# TODO: throttle parameter?
# TODO: Amazon query?
# TODO: output in other formats?

__docformat__ = 'restructuredtext en'


### IMPORTS ###

import logging
import sys, re
from os import path, rename
from optparse import OptionParser
from exceptions import BaseException

from biblio.webquery import errors
from config import *
from common import *


### CONSTANTS & DEFINES ###

ISBN10_PAT = r'(\d{9}[\d|X])'
ISBN13_PAT = r'(\d{13})'

ISBN_PATS = [
	r'\(ISBN([^\)]+)\)',
	r'^(\d{13})$',
	r'^(\d{13})[\b|_|\.|\-|\s]',
	r'[\b|_|\.|\-|\s](\d{13})$',
	r'[\b|_|\.|\-|\s](\d{13})[\b|_|\.]',
	r'^(\d{9}[\d|X])$',
	r'^(\d{9}[\d|X])[\b|_|\.|\s|\-]',
	r'[\b|_|\.|\-|\s](\d{9}[\d|X])$',
	r'[\b|_|\.|\-|\s](\d{9}[\d|X])[\b|_|\.|\-|\s]',
	r'ISBN\s*(\d{13})',
	r'ISBN\s*(\d{9}[\d|X])',
	r'[\[\(](\d{9}[\d|X])[\]\)]',
	r'\D(\d{13})$',
	r'\D(\d{9}[\d|X])$',

]

ISBN_RE = [re.compile (p, re.IGNORECASE) for p in ISBN_PATS]

_DEV_MODE = True

DEF_NAME_FMT = '%(auth)s%(year)s_%(short_title)s_(isbn%(isbn)s)'
DEF_STRIP_CHARS = ''':!,'".?()'''
DEF_BLANK_CHARS = ''
STRIP_CHARS_RE = re.compile ('[\'\":\,!\.\?\(\)]')

COLLAPSE_SPACE_RE = re.compile (r'\s+')


CASE_CHOICES = [
	'orig',
	'upper',
	'lower',
]


### IMPLEMENTATION ###

def parse_args():
	# Construct the option parser.
	usage = '%prog [options] FILES ...'
	version = "version %s" %  script_version
	description='Extract an ISBN from a file name, look up the associated ' \
		'bibliographic information in a webservice and rename the file ' \
		'appropriately.'
	epilog='ISBNs are extracted from filenames by pure heuristics - obviously ' \
		'not all forms will be found. ' \
		'The new name is generated first before the various processing ' \
		'options are applied. In order, characters are stripped from the ' \
		'name, excess whitespace is collapsed and then the case conversion ' \
		'is applied. The file extension, if any, is removed before renaming ' \
		'and re-applied afterwards. ' \
		'We suggest you try a dryrun before renaming any files.'
	optparser = OptionParser (usage=usage, version=version, epilog=epilog,
		description=description)
	add_shared_options (optparser)

	optparser.add_option ('--case', '-c',
		dest='case',
		help="Case conversion of the new file name. Choices are %s." \
			"The default is %s. " % (', '.join (CASE_CHOICES), CASE_CHOICES[0]),
		choices=CASE_CHOICES,
		default=CASE_CHOICES[0],
	),
	
	optparser.add_option ('--leave_whitespace',
		action='store_true',
		dest='leave_whitespace',
		help="Leave excess whitespace. By default, consecutive spaces in " \
			"names are compacted",
		default=False,
	)
	
	optparser.add_option ('--replace_whitespace',
		dest='replace_whitespace',
		help="Replace whitespace in the new name with this string.",
		default='',
	)
	
	optparser.add_option ('--strip_chars',
		dest='strip_chars',
		help="Remove these characters from the new name. By default " \
			"this are '%s'." % DEF_STRIP_CHARS,
		default=DEF_STRIP_CHARS,
	)
	
	optparser.add_option ('--overwrite',
		action='store_true',
		dest='overwrite',
		help="Overwrite existing files.",
		default=False,
	)
	
	optparser.add_option ('--dryrun',
		action='store_true',
		dest='dryrun',
		help="Check function and without renaming files.",
		default=False,
	)
	
	optparser.add_option ('--template',
		dest='template',
		help="The form to use for renaming the file. The fields recognised are " \
			"auth (primary authors family name), " \
			"title (full title of the book), " \
			"short_title (abbreviated title), " \
			"isbn, " \
			"year (year of publication). The default is '%s'." % DEF_NAME_FMT,
		default=DEF_NAME_FMT,
	)
	
	optparser.add_option ('--unknown',
		dest='unknown',
		help="Use this string if value is undefined.",
		default='unknown',
	)
	
	# parse and check args
	options, fpaths = optparser.parse_args()
	
	if (not fpaths):
		optparser.error ('No files specified')
	check_shared_options (options, optparser)
	
	## Postconditions & return:
	return fpaths, options


def dir_base_ext_from_path (fpath):
	"""
	Return a files base name and extension from it's path.
	"""
	fdir, fname = path.split (fpath)
	base, ext = path.splitext (fname)
	return fdir, base, ext


def rename_file (oldpath, newname):
	"""
	Rename a file, while keeping it in the same location.
	"""
	fdir, fname = path.split (oldpath)
	newpath = path.join (fdir, newname)
	rename (oldpath, newpath)


def extract_isbn_from_filename (fname):
	for r in ISBN_RE:
		match = r.search (fname)
		if match:
			return match.group(1)
	return None
	

def generate_new_name (bibrec, options):
	if (bibrec.authors):
		primary_auth = bibrec.authors[0]
		auth_str = primary_auth.family or primary_auth.given
	else:
		auth_str = options.unknown
	logging.info ('~ found %s - %s' % (auth_str, bibrec.title))
	return options.template % {
		'auth': auth_str,
		'year': bibrec.year or options.unknown,
		'short_title': bibrec.short_title or options.unknown,
		'title': bibrec.title or options.unknown,
		'isbn': bibrec.id or options.unknown,
	}
	
	
def postprocess_name (name, options):
	## Preconditions:
	assert (name)
	## Main:
	# strip chars from name
	for c in options.strip_chars:
		name = name.replace (c, '')
	# clean up excess whitespace
	if (not options.leave_whitespace):
		name = COLLAPSE_SPACE_RE.sub (' ', name.strip())
	if (options.replace_whitespace):
		name = name.replace (' ', options.replace_whitespace)
	# harmomise case
	if (options.case == 'lower'):
		name = name.lower()
	elif (options.case == 'upper'):
		name = name.upper()
	## Return:
	return name


def main():
	fpath_list, options = parse_args()
	logging.basicConfig (level=logging.INFO, stream=sys.stdout,
		format= "%(message)s")
	try:
		webqry = construct_webquery (options.webservice, options.service_key)
		for fpath in fpath_list:
			logging.info ('Original %s ...' % fpath)
			fdir, base, ext = dir_base_ext_from_path (fpath)
			isbn = extract_isbn_from_filename (base)
			logging.info ('~ extracted ISBN %s ...' % isbn)
			if (isbn):
				try:
					bibrec_list = webqry.query_bibdata_by_isbn (isbn,
						format='bibrecord')
					if (bibrec_list):
						bibinfo = bibrec_list[0]
						new_name = generate_new_name (bibinfo, options)
						new_name = postprocess_name (new_name, options)
						logging.info ('~ new name %s.' % new_name)
						newpath = path.join (fdir, new_name + ext)
						logging.info ('~ new path %s.' % newpath)
						rename_file = not (options.dryrun)
						if (path.exists (newpath)):
							logging.info ('~ path already exists')
							if not options.overwrite:
								rename_file = False
						if (rename_file):
							logging.info ('~ renaming file')
							rename (fpath, newpath)
					else:
						logging.info ('- no records returned')
				except errors.QueryError, err:
					logging.info ('- query failed: %s.' % err)
			else:
				print logging.info ('- no isbn extracted')
		
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
