#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Querying the ISBNDb for bibliographic information.
"""
# TODO: error-handling logic is correct?

__docformat__ = 'restructuredtext en'


### IMPORTS ###

from impl import ElementTree, assert_or_raise
from basewebquery import BaseKeyedWebQuery
import errors
import utils
from bibrecord import *

__all__ = [
	'IsbndbQuery',
	'isbndb_xml_to_bibrecords',
]


### CONSTANTS & DEFINES ###

ISBNDB_ROOTURL = 'http://isbndb.com/api/books.xml?access_key=%(key)s&'
ISBNDB_KEY = 'OPNH8HG2'

FORMATS = [
	'xml',
	'bibrecord',
]


### IMPLEMENTATION ###

class IsbndbQuery (BaseKeyedWebQuery):
	
	def __init__ (self, key, timeout=5.0, limits=None):
		"""
		C'tor, accepting an access key.
		"""
		BaseKeyedWebQuery.__init__ (self, root_url=ISBNDB_ROOTURL, key=key,
			timeout=timeout, limits=limits)

	def query_service (self, index, value, results):
		"""
		A generalised query for ISBNdb.
		
		:Parameters:
			index : string
				The index to search in ISBNdb.
			value : string
				The value to search for in the index..
			results : iterable
				A list of the data to include in the response.
		
		:Returns:
			The response received from the service.
		
		This serves a general way of accessing all the methods available for
		ISBNdb. It also normalises the ISBN to a suitable form for submission.
		Note that it is probably possible to form a bad query with the wrong
		combination of parameters.
		
		"""
		## Preconditions & preparation:
		if (index == 'isbn'):
			value = utils.normalize_isbn (value)
		## Main:
		sub_url = 'index1=%(indx)s&value1=%(val)s' % {
			'indx': index,
			'val': value,
		}
		if (results):
			res_str = ','.join (list(results))
			sub_url += '&results=' + res_str
		return self.request (sub_url)
		
	def query_bibdata_by_isbn (self, isbn, format='bibrecord'):
		"""
		Return publication data based on ISBN.
		
		:Parameters:
			isbn : string
				An ISBN-10 or ISBN-13.
				
			format : string
				The desired format for the results.
				
		:Returns:
			Publication data in Xisbn XML format.
		
		"""
		## Preconditions & preparation:
		# check and select appropriate format
		assert (format in FORMATS), \
			"unrecognised format '%s', must be one of %s" % (format, FORMATS)
		## Main:
		results = self.query_service (index='isbn', value=isbn, results=[
			'authors', 'subjects', 'texts', 'details'])
		if (format is 'bibrecord'):
			results = isbndb_xml_to_bibrecords (results)
		## Postconditions & return:
		return results

	def query_author_by_name (self, name, fields=None):
		"""
		Search author data based on name.
		
		:Parameters:
			name : string
				The name to search for.
				
			fields : iterable
				What result blocks to return..
				
		:Returns:
			Publication data in ISBNdb XML format.
		
		"""
		## Main:
		results = self.query_service (index='name', value=name, results=fields)
		## Postconditions & return:
		return results

	def query_author_by_id (self, auth_id, fields=None):
		"""
		Search author data based on ID.
		
		:Parameters:
			auth_id : string
				The ISBN "person_id" to search for.
				
			fields : iterable
				What result blocks to return..
				
		:Returns:
			Publication data in ISBNdb XML format.
		
		"""
		## Main:
		results = self.query_service (index='person_id', value=name, results=fields)
		## Postconditions & return:
		return results


def isbndb_xml_to_bibrecords (xml_txt):
	## Main:
	# turn into an xml tree
	root = ElementTree.fromstring (xml_txt)
	assert_or_raise (root.tag == 'ISBNdb', errors.ParseError,
		"ISBNdb document root should be 'ISBNdb', not '%s'" % root.tag)
	assert_or_raise (len (root) == 1, errors.ParseError,
		"ISBNdb document root has wrong number of children (%s)" % len (root))
	# grab list result
	booklist_elem = root[0]
	assert_or_raise (booklist_elem.tag == 'BookList', errors.ParseError,
		"ISBNdb document should contain 'BookList', not '%s'" %
		booklist_elem.tag)
	# for every result ...
	bibrecs = []
	for bdata in booklist_elem.findall ('BookData'):
		newrec = BibRecord()
		newrec.pubtype = 'book'
		newrec.title = (bdata.findtext ('TitleLong') or u'').strip()
		newrec.abstract = (bdata.findtext ('Summary') or u'').strip()
		newrec.note = (bdata.findtext ('Notes') or u'').strip()
		newrec.keywords = [e.text.strip() for e in bdata.findall ('Subject')]
		authors = []
		author_elem = bdata.find ('Authors')
		if (author_elem):
			author_strs = [e.text.strip() for e in author_elem.findall
				('Person')]
			authors = [utils.parse_single_name (a) for a in author_strs]
		else:
			author_elem = bdata.find ('AuthorsText')
			if (author_elem):
				edited, authors_str = utils.parse_editing_info (author_elem.text)
				newrec.edited = edited
				authors = utils.parse_names (authors_str)
		newrec.authors = authors
		newrec.id = bdata.attrib['isbn']
		pub_elem = bdata.find ('PublisherText')
		if (pub_elem):
			newrec.publisher, newrec.city, newrec.year = \
				parse_publisher (pub_elem.text)
		bibrecs.append (newrec)
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
