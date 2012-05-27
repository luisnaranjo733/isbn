#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classes for throttling web-queries, so as to stay within limits.
"""
# TODO: error-handling logic is correct?

__docformat__ = 'restructuredtext en'


### IMPORTS ###

import time
from exceptions import ValueError, RuntimeError

import impl
import errors


### CONSTANTS & DEFINES ###

FAIL_AND_RAISE = 'RAISE'
FAIL_AND_WAIT = 'WAIT'


### IMPLEMENTATION ###

class BaseQueryThrottle (impl.ReprObj):
	"""
	A limit upon query usage. 
	
	Often webservices will request that users restrict themselves to a request
	every second, or no more than 1000 a day, etc. This is a base class for
	implementing those limits. Different restrictions can be implemented in
	derived classes.
	
	Limits are constructed with set behaviour 
	
	"""
	# TODO: introduce special handlers for various failure actions?
	
	_repr_fields = [
		'fail_action',
		'wait_duration',
	]
	
	def __init__ (self, fail_action=None, wait_duration=1.0):
		"""
		Ctor, allowing the polling period and failure behaviour to be set.
		
		"""
		self.fail_action = fail_action or FAIL_AND_RAISE
		self.wait_duration = wait_duration
		
	def check_limit (self, wquery):
		"""
		Has the query exceeded its limit?
		
		:Parameters:
			wquery
				The object or service to be throttled. This allows the same limit
				to service several objects in different ways (e.g. by having them
				share the same limit, or be handled independently).
				
		:Returns:
			A boolean, giving whether the query is within limit or not.
		
		This is a primarily internal method for testing whether a limit has been
		reached. Handling that circumstance is left to the calling method
		`check_limit`. This should be overridden in derived class to implement
		different throttling methods.
				
		"""
		if (self.within_limit (wquery)):	
			self.log_success (wquery)	
		else:
			if (self.fail_action == FAIL_AND_RAISE):
				raise errors.QueryThrottleError()
			elif (self.fail_action == FAIL_AND_WAIT):
				time.sleep (self.wait_duration)
				while (not self.within_limit (wquery)):
					time.sleep (self.wait_duration)
				self.log_success (wquery)	
			else:
				raise ValueError ("unrecognised fail action '%s'" %
					self.fail_action)
				
	def within_limit (self, wquery):
		"""
		Has the query exceeded its limit?
		
		:Parameters:
			wquery
				See `check_limit`
		
		This should be called by services to test whether a limit has been
		reached. Handling that circumstance is left to the calling method
		`check_limit`. This should be overridden in derived class to implement
		different throttling methods.
		
		"""
		return True
		
			
	def log_success (self, wquery):
		"""
		Sucessful queries will probably effect the success of future ones, so
		here is a place to log them.
		"""
		pass	
			
		
class WaitNSecondsThrottle (BaseQueryThrottle):
	"""
	Limit a query to every N seconds at most.
	
	By default this throttle holds the query until the wait period is over.
	Note that this throttle can be used across a set of queries, so that the
	limit applies for the set. In this case the waiting behaviour could be
	undesirable, with a large population of queries on hold.
	
	"""
	def __init__ (self, wait, fail_action=FAIL_AND_WAIT):
		"""
		C'tor, allowing the wait period and failure behaviour to be set.
		
		:Parameters:
			wait : int or float
				The period to enforce between queries.
			fail_action
				See `BaseQueryThrottle`.
				
		"""
		BaseQueryThrottle.__init__ (self, fail_action)
		self.wait = wait
		self._prev_time = 0

	def within_limit (self, wquery):
		"""
		Has it been longer than the wait period since the last query?
		
		"""
		return (self.wait < (time.time() - self._prev_time))

	def log_success (self, wquery):
		self._prev_time = time.time()
		
		
class WaitOneSecondThrottle (WaitNSecondsThrottle):
	"""
	Limit a query to once every second at most.
	
	This is a common limit, and so is provided as a convenience.
	
	"""
	def __init__ (self, fail_action=FAIL_AND_WAIT):
		WaitNSecondsThrottle.__init__ (self, wait=1.0, fail_action=fail_action)


class AbsoluteNumberThrottle (BaseQueryThrottle):
	"""
	Limit a query to a maximum number.

	Many web-services have a per-day query limit (e.g. 500 per day for ISBNdb).
	It is difficult to implement this across multiple invocations of the
	query objects and Python interpreter, but this can serve as a crude
	implementation. By default, it raises an exception if the limit is
	reached.

	"""
	def __init__ (self, max, fail_action=FAIL_AND_RAISE):
		"""
		C'tor, allowing the maximum queries and failure behaviour to be set.

		:Parameters:
			max : int
				The total number of queries allowed.
			fail_action
				See `BaseQueryThrottle`.

		"""
		BaseQueryThrottle.__init__ (self, fail_action)
		self.max = max
		self._query_count = 0

	def within_limit (self, wquery):
		"""
		Have fewer queries been posted than the limit?

		Note that if multiple queries simulatanoeusly test via this function,
		exceeding the limit is possible.
		
		"""
		return (self._query_count < self.max)

	def log_success (self, wquery):
		self._query_count += 1
		
	
class Max500Throttle (object):
	"""
	Limit a query to 500 attempts at most.
	
	This is a common limit, and so is provided as a convenience.
	
	"""
	def __init__ (self):
		AbsoluteNumberThrottle.__init__ (self, 500)


		
### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ######################################################################
