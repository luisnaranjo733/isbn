#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Querying WorldCat xISBN service for bibliographic information.

"""
# TODO: error-handling logic is correct?

__docformat__ = 'restructuredtext en'


### IMPORTS ###

import re

from basewebquery import BaseWebquery
from bibrecord import BibRecord
import utils
from errors import *

__all__ = [
	'XisbnQuery',
	'xisbn_py_to_bibrecord',
]


### CONSTANTS & DEFINES ###

XISBN_ROOTURL = 'http://xisbn.worldcat.org/webservices/xid/isbn/'

FORMATS = [
	'xml',
	'html',
	'json',
	'python',
	'ruby',
	'php',
	'csv',
	'txt',
	'bibrecord',
]


### IMPLEMENTATION ###

class XisbnQuery (BaseWebquery):
	
	def __init__ (self, timeout=5.0, limits=None):
		"""
		C'tor.
		"""
		BaseWebquery.__init__ (self, root_url=XISBN_ROOTURL, timeout=5.0,
			limits=None)

	def query_service (self, isbn, method, format, fields=['*']):
		"""
		A generalised query for xISBN.
		
		:Parameters:
			isbn : string
				A normalised ISBN-10 or -13.
			method : string
				The request type to make of xISBN.
			format : string
				The form for the response.
			fields : iterable
				A list of the fields to include in the response.
		
		:Returns:
			The response received from the service.
		
		This serves a general way of accessing all the methods available for
		xISBN. It also normalises the ISBn to a suitable form for submission.
		
		"""
		## Preconditions & preparation:
		assert (format in FORMATS), \
			"unrecognised format '%s', must be one of %s" % (format, FORMATS)
		## Main:
		sub_url = "%(isbn)s?method=%(mthd)s&format=%(fmt)s&fl=%(flds)s" % {
			'mthd': method,
			'fmt': format,
			'isbn': utils.normalize_isbn (isbn),
			'flds': ','.join (fields),
		}
		return self.request (sub_url)
		
	def query_bibdata_by_isbn (self, isbn, format='bibrecord'):
		"""
		Return publication data based on ISBN.
		
		:Parameters:
			isbn : string
				An ISBN-10 or ISBN-13.
				
		:Returns:
			Publication data in Xisbn XML format.
		
		"""
		## Preconditions & preparation:
		# select appropriate format
		fmt_map = {
			'bibrecord': 'python',
		}
		passed_fmt = fmt_map.get (format, format)
		## Main:
		results = self.query_service (isbn=isbn, method='getMetadata',
			format=passed_fmt)
		if (format == 'bibrecord'):
			results = xisbn_py_to_bibrecord (results)
		## Postconditions & return:
		return results
	
	def query_editions_by_isbn (self, isbn, format='xml'):
		"""
		Return the editions associated with an ISBN.
		
		:Parameters:
			isbn : string
				An ISBN-10 or ISBN-13.
			format : string
				See `query_service`. 
				
		:Returns:
			Publication data in Xisbn XML format.
		
		"""
		## Main:
		return self.query_service (isbn=isbn, method='getEditions',
			format=format)
	
	def query_isbn (self, isbn, method, format='string'):
		"""
		A generalised method for ISBN queries that return ISBNs.
		
		This allows functionality to be shared among the ISBN conversion and
		checking methods.
		
		"""
		## Preconditions & preparation:
		# check and select appropriate format
		fmt_map = {
			'string': 'python',
		}
		passed_fmt = fmt_map.get (format, format)
		## Main:
		results = self.query_service (isbn=isbn, method=method,
			format=passed_fmt)
		if (format == 'string'):
			results = xisbn_py_to_list (results)
			results = [d['isbn'] for d in results]
		## Postconditions & return:
		return results
	
	def query_isbn10_to_13 (self, isbn, format='string'):
		## Main:
		return self.query_isbn (isbn=isbn, method='to13',
			format=format)
	
	def query_isbn13_to_10 (self, isbn, format='string'):
		## Main:
		return self.query_isbn (isbn=isbn, method='to10',
			format=format)

	def query_fix_isbn_csum (self, isbn, format='string'):
		## Main:
		return self.query_isbn (isbn=isbn, method='fixChecksum',
			format=format)

	def query_hyphenate_isbn (self, isbn, format='string'):
		## Main:
		return self.query_isbn (isbn=isbn, method='hyphen',
			format=format)



def xisbn_py_to_list (pytxt):
	"""
	Translate the Python text returned by xISBN to a list of dicts.
	
	:Parameters:
		pytxt : string
			An Xisbn record in Python.
			
	:Returns:
		A list with a dictionary for each record.
		
	"""
	## Main:
	# convert to python structures
	xisbn_dict = eval (pytxt)
	# parse reply status - if the query term was unknown (but valid) return
	# a empty list for no records
	status = xisbn_dict.get ('stat', 'ok')
	if (status != 'ok'):
		if (status == 'unknownId'):
			return []
		else:
			raise QueryError ("response status was bad (%s)" % status)
	## Postconditions & return:
	return xisbn_dict['list']

	
def xisbn_py_to_bibrecord (pytxt):
	"""
	Translate the Python text returned by xISBN to a series of BibRecords.
	
	:Parameters:
		pytxt : string
			An Xisbn record in Python.
			
	:Returns:
		A list of BibRecords.
		
	"""
	## Main:
	# convert to python structures
	records = xisbn_py_to_list (pytxt)
	# parse individual records
	bibrecs = []
	for entry in records:
		new_bib = BibRecord()
		new_bib.publisher = entry.get ('publisher', '')
		new_bib.lang = entry.get ('lang', '')
		new_bib.city = entry.get ('city', '')
		auth_str = entry.get ('author', '')
		edited, auth_str = utils.parse_editing_info (auth_str)
		new_bib.edited = edited
		auth_list = utils.parse_names (auth_str)
		new_bib.authors = auth_list
		new_bib.year = entry.get ('year', '')
		new_bib.id = entry.get ('isbn', [''])[0]
		new_bib.add_ext_references ('isbn', entry.get ('isbn', []))
		new_bib.add_ext_references ('lccn', entry.get ('lccn', []))
		new_bib.add_ext_references ('oclcnum', entry.get ('oclcnum', []))
		new_bib.title = entry.get ('title', '')
		form = entry.get ('form', [''])[0].upper()
		if (form in ['BA', 'BB', 'BC']):
			if (edited):
				new_bib.type = 'collection'
			else:
				new_bib.type = 'book'
		else:
			# AA (Audio), DA (Digital),FA (Film), MA (Microform), VA (Video)
			new_bib.type = 'misc'	
		bibrecs.append (new_bib)
	## Postconditions & return:
	return bibrecs



### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ######################################################################
