#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classes for representing bibliographic records and authors.

These are not the intended major function of this module, but are necessary for translation
between formats.

Variously based upon:

* pymarc
* bibconverter
* bibliograph.core and bibliograph.parsing

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

import re

from biblio.webquery import impl


### CONSTANTS & DEFINES ###

SHORT_TITLE_SPLIT_RE = re.compile ('[:\?]')


### IMPLEMENTATION ###

class BibRecord (impl.ReprObj):
	# TODO: maybe need url, doi, language, ISBN/ISSN, volume, number, pages,
	# month, booktitle, pubcity, address
	_repr_fields = [
		'id',
		'type',
		'lang',
		'title',
		'authors',
		'year',
		'edited',
		'abstract',
		'keywords',
		'publisher',
		'journal',
		'note',
		'ext_references',
	]
	def __init__ (self):
		"""
		C'tor.
		"""
		self.id = u''
		self.type = u''
		self.title = u''
		self.lang = u''
		self.authors = []
		self.year = None
		self.edited = False
		self.abstract = u''
		self.keywords = []
		self.publisher = u''
		self.journal = u''
		self.note = u''
		self.ext_references = {}
		
	def add_ext_references (self, key, val):
		refs = self.ext_references.get (key, [])
		refs.extend (list (val))
		self.ext_references[key] = refs
		
	def get_short_title (self):
		match = SHORT_TITLE_SPLIT_RE.search (self.title)
		if (match):
			return self.title[:match.start()].strip()
		else:
			return self.title
		
	short_title = property (get_short_title)



class PersonalName (impl.ReprObj):
	"""
	A name, as used for authors and editors.
	
	The terms 'given', 'other' and 'family' are used in preference to other
	schemes, as they are more culture-neutral and do not assume any particular
	ordering.
	
	given
		The first / christian or forename, e.g. 'John'.
	other
		Any middle names, e.g. 'James Richard'.
	family
		surname, last name, e.g. 'Smith'.

	"""
	# TODO: properties for 'middle', 'surname' etc.
	
	_repr_fields = [
		'prefix',
		'title',
		'given',
		'other',
		'family',
		'suffix',
	]
	
	def __init__ (self, given, other=None, family=None, title=None,
			prefix=None, suffix=None):
		"""
		C'tor, requiring only the given name.
		
		Note that the only required argument is the given name, allowing single
		names (e.g. 'Madonna'). Also the order of positional arguments allows a
		a regular name to be passed as 'John', 'James', 'Smith'. 
	
		"""
		self.given = given
		self.other = other
		self.family = family
		self.title = title
		self.prefix = prefix
		self.suffix = suffix
		
	def __unicode__ (self):
		"""
		Return a readable formatted version of the name.
		"""
		fields = [getattr (self, f, '') for f in self._repr_fields]
		return u' '.join ([f for f in fields if f])
	
	def __repr__ (self):
		"""
		Return a representation of this object.
		"""
		# overrides base class because that calls __unicode__
		return impl.ReprObj.__repr__ (self)



### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ######################################################################
