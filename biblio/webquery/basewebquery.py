#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
A base class for querying webservices.
"""
# TODO: list of possible apis at http://techessence.info/apis and
# http://www.programmableweb.com/apitag/books#


__docformat__ = 'restructuredtext en'


### IMPORTS ###

import socket
from urllib import urlopen, quote

import impl


### CONSTANTS & DEFINES ###

### IMPLEMENTATION ###

class BaseWebquery (impl.ReprObj):
	"""
	A base class for querying webservices.
	
	This serves as a foundation for other web-query classes, centralising a
	small amount of functionality and providing a common interface.
	
	"""
	
	_repr_fields = [
		'root_url',
		'timeout',
		'limits',
	]
	
	def __init__ (self, root_url, timeout=5.0, limits=[]):
		"""
		Ctor, allowing the setting of the webservice, timeout and limits on use.
		
		:Parameters:
			root_url : string
				The url to be used as the basis for all requests to this service.
				It should be the common "stem" that does not vary for any request.
			timeout : int or float
				How many seconds to wait for a response.
			limits : iterable
				A list of QueryThrottles to impose upon the use of this webservice.
		
		"""
		self.root_url = root_url
		self.timeout = timeout
		self.limits = limits or []

	def request (self, sub_url):
		"""
		Send a request to the webservice and return the response.
		
		:Parameters:
			sub_url : string
				This will be added to the root url set in the c'tor and used as the
				actual url that is requested.
		
		:Returns:
			The data in the webservice response.
		
		This is the low-level calls that checks any throttling, send the request
		and actually fetches the response data. For consistency, all service
		access should be placed through here.
		
		"""
		for limit in self.limits:
			limit.check_limit (self)
		socket.setdefaulttimeout (self.timeout)
		full_url = self._build_request_url (sub_url)
		return urlopen (full_url).read()
	
	def _build_request_url (self, sub_url):
		"""
		Assemble the full url for requesting data.
		
		:Parameters:
			sub_url : string
				The later part of a request url that can change.
		
		:Returns:
			The url to be used for the webservice request.
		
		This is an internal method, intended for over-riding or modifying the
		request construction in subclasses, for example where an access key must
		be included.
		
		"""
		return self.root_url + sub_url


class BaseKeyedWebQuery (BaseWebquery):
	"""
	A Webquery that requires an access key.
	"""
	def __init__ (self, root_url, key, timeout=5.0, limits=[]):
		"""
		Ctor, allowing the setting of a webservice access key.
		
		:Parameters:
			root_url
				See `BaseWebquery`. Either this or the sub_url passed to `request`
				must include a keyword formatting for the access key, i.e.
				``%(key)s``.
			key : string
				The access or PAI key to be passed to the webservice for access.
			timeout
				See `BaseWebquery`.
			limits
				See `BaseWebquery`.
		
		"""
		BaseWebquery.__init__ (self, root_url=root_url, timeout=timeout,
			limits=limits)
		self.key = key
	
	def _build_request_url (self, sub_url):
		"""
		Assemble the full url for requesting data.
		
		:Parameters:
			sub_url : string
				See `BaseWebquery`.
		
		:Returns:
			The url to be used for the webservice request, including the
			access key.
		
		This builds the url for any request, including the access key. Either
		the root_url passed to the c'tor or the sub_url passed to the request
		must include keyword formatting for the access key, i.e. ``%(key)s``.
		
		"""
		full_url = self.root_url + sub_url
		return full_url % {'key': self.key}

	
### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ######################################################################
