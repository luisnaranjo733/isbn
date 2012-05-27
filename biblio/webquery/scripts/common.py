#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Function shared between the scripts.

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

from biblio.webquery.basewebquery import *
from config import *

try:
	from biblio.webquery import __version__ as script_version
except:
	script_version = 'unknown'

__all__ = [
	'script_version',
	'add_shared_options',
	'check_shared_options',
	'construct_webquery',
]


### CONSTANTS & DEFINES ###

### IMPLEMENTATION ###

def add_shared_options (optparser):
	optparser.add_option ('--debug',
		dest="debug",
		action='store_true',
		help='For errors, issue a full traceback instead of just a message.',
	)
	
	optparser.add_option ('--service', '-s',
		dest='webservice',
		help="The webservice to query. Choices are %s. The default is %s." % (
			', '.join (['%s (%s)' % (s['id'], s['title']) for s in WEBSERVICES]),
			DEFAULT_WEBSERVICE['id']
		) ,
		metavar='SERVICE',
		choices=WEBSERVICE_LOOKUP.keys(),
		default=DEFAULT_WEBSERVICE['id'],
	)
	
	optparser.add_option ('--key', '-k',
		dest="service_key",
		help='''The access key for the webservice, if one is required.''',
		metavar='KEY',
		default=None,
	)


def check_shared_options (options, optparser):
	serv = WEBSERVICE_LOOKUP.get (options.webservice, None)
	if (not serv):
		optparser.error ("Unrecognised webservice '%s'" % options.webservice)
	if (issubclass (serv['ctor'], BaseKeyedWebQuery)):
		if (not options.service_key):
			optparser.error ("%s webservice requires access key" % serv['title'])
	else:
		if (options.service_key):
			optparser.error ("%s webservice does not require access key" %
				serv['title'])


def construct_webquery (service, key):
	serv_cls = WEBSERVICE_LOOKUP[service]['ctor']
	if (issubclass (serv_cls, BaseKeyedWebQuery)):
		return serv_cls (key=key, timeout=5.0, limits=None)
	else:
		return serv_cls (timeout=5.0, limits=None)

	
	
### TEST & DEBUG ###

### MAIN ###

if __name__ == '__main__':
	main()
	

### END ######################################################################
