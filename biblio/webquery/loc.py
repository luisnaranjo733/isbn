#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Querying the Library of Congress for bibliographic information.
"""
# TODO: error-handling logic is correct?

__docformat__ = 'restructuredtext en'


### IMPORTS ###

from basewebquery import BaseWebquery
import querythrottle


### CONSTANTS & DEFINES ###

LOC_ROOTURL = \
	'http://z3950.loc.gov:7090/voyager?operation=searchRetrieve&version=1.1'


### IMPLEMENTATION ###

class LocQuery (BaseWebquery):
	
	def __init__ (self, timeout=5.0, limits=None):
		"""
		C'tor.
		"""
		root_url = LOC_ROOTURL % {'key': key}
		BaseWebquery.__init__ (self, root_url=root_url,timeout=timeout,
			limits=limits)
		
	def query_bibdata_by_isbn (self, isbn, format='MODS'):
		"""
		Return the metadata for a publication specified by ISBN.
		"""
		format = lower (format)
		assert (format in ['mods', 'opacxml', 'dc', 'marcxml'])
		sub_url = '&recordSchema=%(format)s&startRecord=1&maximumRecords=5&' \
			'query=bath.standardIdentifier=%(isbn)s'  % {
				'isbn': isbn,
				'format': format,
			}
		return self.query (sub_url)




### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ######################################################################
