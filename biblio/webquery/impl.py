#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Various (fragile) implementation details and utilities.

Don't reply on these because they may go away.

"""
# TODO: error-handling logic is correct?

__docformat__ = 'restructuredtext en'


### IMPORTS ###

try: 
	from xml.etree import ElementTree
except:
	from elementtree import ElementTree

__all__ = [
	'ElementTree',
	'ReprObj',
	'normalize_isbn',
	'assert_or_raise',
]


### CONSTANTS & DEFINES ###

### IMPLEMENTATION ###

class ReprObj (object):
	"""
	A class with an simple and consistent printable version.
	"""
	_repr_fields = [
		# override in derived classes
	]
	
	def __str__ (self):
		return self.__unicode__().encode ('utf8')
	
	def __unicode__ (self):
		repr_strs = ["%s: '%s'" % (field, getattr (self, field)) for field in
			self._repr_fields]
		return "%s (%s)" % (self.__class__.__name__, '; '.join (repr_strs))
	
	def __repr__ (self):
		return str (self)


def assert_or_raise (cond, error_cls, error_msg=None):
	"""
	If a condition is not met, raise a assertion with this message.
	"""
	if (not cond):
		if error_msg:
			error = error_cls (error_msg)
		else:
			error = error_cls()
		raise error


### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ######################################################################
