#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Various utilities.

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

import re

from bibrecord import PersonalName


### CONSTANTS & DEFINES ###

# patterns for extracting editors names
EDITOR_PATS = [re.compile (x, flags=re.IGNORECASE+re.UNICODE) for x in
	[
		r'^edited by\s+',   # "(edited )by ..."
		r'\s*, editors\.?$',     # "..., editors"
		r'^editors,?\s*',        # "editors, ..."        
	]
]

# patterns for extracting author info
STRIP_PATS = [re.compile (x, flags=re.IGNORECASE+re.UNICODE) for x in
	[
		r'^by\s+',   # "by ..."
		r'\s*;\s+with an introduction by .*$',
		r'^\[\s*',               
		r'\s*\]$',
		r'\.{3,}',               # "..."
		r'et[\. ]al\.',          # "et al."
		r'\[',
		r'\]',
		r'\([^\)]+\)', 
		r'\s*;.*$',
	]
]
AND_PAT = re.compile (r'\s+and\s+')
COLLAPSE_SPACE_RE = re.compile (r'\s+')

PUBLISHER_RES = [re.compile (p, flags=re.IGNORECASE+re.UNICODE) for p in
	[
		'^(?P<city>.*)\s*:\s*(?P<pub>.*)\s*,\s*c?(?P<year>\d{4})\.?$',
		'^(?P<pub>.*)\.?$',
	]
]

### IMPLEMENTATION ###

def normalize_isbn (isbn):
	"""
	Remove formatting from an ISBN, making it suitable for web-queries.
	"""
	return isbn.replace (' ', '').replace ('-', '').lower().strip()


def parse_single_name (name_str):
	"""
	Clean up an indivdual name into a more consistent format.
	"""
	family = given = other = ''
	# normalise space
	name_str = COLLAPSE_SPACE_RE.sub (' ', name_str.strip())
	# break into parts
	if (', ' in name_str):
		# if [family], [given] [other]
		name_parts = name_str.split (', ', 1)
		family = name_parts[0].strip()
		given_other = name_parts[1].split (' ', 1)
		given = given_other[0]
		other = given_other[1:]
	else:
		# if [given] [other] [family]
		name_parts = name_str.split (' ')
		given = name_parts[0]
		other_family = name_parts[1:]
		# the 'Madonna' clause
		if (other_family):
			family = other_family[-1]
			other = ' '.join (other_family[:-1])
	# some tidying up
	if (family.endswith ('.')):
		family = family[:-1]
	# create name
	name = PersonalName (given)
	name.family = family or ''
	name.other = other or ''
	## Postconditions & return:
	return name
	
			
def parse_names (name_str):
	"""
	Clean up a list of names into a more consistent format.

	:Parameters:
		name_str : string
			The "author" attribute from a Xisbn record in XML.
	
	:Returns:
		A list of the authors in "reverse" format, e.g. "['Smith, A. B.',
		'Jones, X. Y.']"

	Xisbn data can be irregularly formatted, unpredictably including
	ancillary information. This function attempts to cleans up the author field
	into a list of consistent author names.
	
	For example::

		>>> n = parse_names ("Leonard Richardson and Sam Ruby.")
		>>> print (n[0].family == 'Richardson')
		True
		>>> print (n[0].given == 'Leonard')
		True
		>>> print (not n[0].other)
		True
		>>> n = parse_names ("Stephen P. Schoenberger, Bali Pulendran")
		>>> print (n[0].family == 'Schoenberger')
		True
		>>> print (n[0].given == 'Stephen')
		True
		>>> print (n[0].other == 'P.')
		True
		>>> n = parse_names ("Madonna")
		>>> print (not n[0].family)
		True
		>>> print (n[0].given == 'Madonna')
		True
		>>> print (not n[0].other)
		True
		
	"""
	# TODO: Xisbn authors fields are often appended with extra information
	# like "with a foreword by" etc. Largely these are separated from the
	# author list by semi-colons and so should be easy to strip off.
	
	## Preconditions & preparation:
	# clean up string and return trivial cases 
	name_str = name_str.strip()
	if (not name_str):
		return []
	# strip extraneous and replace 'and'
	for pat in STRIP_PATS:
		name_str = pat.sub ('', name_str)
	name_str = AND_PAT.sub (', ', name_str)
	## Main:
	auth_list = name_str.split (', ')
	name_list = [parse_single_name (x) for x in auth_list]
	## Postconditions & return:
	return name_list
	

def parse_editing_info (name_str):
	"""
	Detect whethers names are editors and returns
	
	Returns:
		Whether editing information was recognised and the name with that
		editing information removed.
		
	For example::

		>>> parse_editing_info ("Leonard Richardson and Sam Ruby.")
		(False, 'Leonard Richardson and Sam Ruby.')
		>>> parse_editing_info ("Ann Thomson.")
		(False, 'Ann Thomson.')
		>>> parse_editing_info ("Stephen P. Schoenberger, Bali Pulendran, editors.")
		(True, 'Stephen P. Schoenberger, Bali Pulendran')
		>>> print parse_editing_info ("Madonna")
		(False, 'Madonna')
	
	"""
	## Preconditions & preparation:
	# clean up string and return trivial cases 
	name_str = name_str.strip()
	if (not name_str):
		return False, ''
	## Main:
	# strip extraneous and replace 'and'
	for pat in EDITOR_PATS:
		match = pat.search (name_str)
		if match:
			return True, pat.sub ('', name_str)
	## Postconditions & return:
	# no editting information found
	return False, name_str
		
		
def parse_publisher (pub_str):
	"""
	Parse a string of publisher information.

	:Parameters:
		pub_str : string
			text giving publisher details.
		
	:Returns:
		A tuple of strings, being (<publisher>, <city of publication>,
		<year of publication>). If no value is available, an empty string
		returned.
		
	As with author names, publication details are often inconsistently set out,
	even in bibliographic data. This function attempts to parse out and
	normalise the details.
	
	For example::
	
		>>> parse_publisher ('New York: Asia Pub. House, c1979.')
		('Asia Pub. House', 'New York', '1979')
		>>> parse_publisher ('New York : LearningExpress, 1999.')
		('LearningExpress', 'New York', '1999')
		>>> parse_publisher ('HarperTorch')
		('HarperTorch', '', '')
		>>> parse_publisher ('Berkeley Heights, NJ: Enslow Publishers, c2000.')
		('Enslow Publishers', 'Berkeley Heights, NJ', '2000')
		
	"""
	for re in PUBLISHER_RES:
		match = re.search (pub_str)
		if match:
			fields = ['pub', 'city', 'year']
			match_vals = match.groupdict (None)
			return tuple ([match_vals.get (f, '').strip() for f in fields])
	return '', '', ''



### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ######################################################################
