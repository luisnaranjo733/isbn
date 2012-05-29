"""An isbn web query API based on http://xisbn.worldcat.org/xisbnadmin/doc/api.htm

Author : Luis Naranjo <luisnaranjo733@hotmail.com>
"""

try:
    import simplejson as json
except ImportError:
    import json

from urllib import urlopen
from pprint import pprint

methods = ['getEditions', 'getMetadata', 'to13', 'to10', 'fixChecksum', 'hyphen']

api_url = 'http://xisbn.worldcat.org/webservices/xid/isbn/{isbn}?method={method}&format=json&fl=*'
#  TODO: Add &ai={affiliate_ID}

"""
Possible Parameters
===================

author: Author
city: City of Publication
ed: Edition
form: The ONIX production form code, this field is space-delimited if multiple values exist. Current supported values include:
AA (Audio), BA (Book), BB (Hardcover), BC (Paperback), DA (Digital),FA (Film or transparency), MA(Microform), VA(Video).

lang: The language field uses three-character MARC Code List for Languages.
lccn: Library Of Congress Control Number, this field is space-delimited if multiple values exist.
oclcnum: OCLC number, this field is space-delimited if multiple values exist.
originalLang: Original Language
publisher: Publisher
title: Title
url: URL link to electronic resource, this field is space-delimited if multiple values exist.
year: Publication year"""

global maximal_parameters, minimal_parameters
minimal_parameters = ['title', 'author', 'publisher', 'year', 'city']
maximal_parameters = ['city', 'ed', 'form', 'lang', 'lccn', 'oclcnum', 'originalLang', 'publisher', 'title', 'url', 'year']


class QueryError(Exception):
    pass


class Book(object):
    def __init__(self, isbn):
        """Takes an ISBN-10 or ISBN-13 as input.

        Attributes are created dynamically.

        Any failed web query will raise a QueryError (isbn.QueryError)

        Consult the docstrings of the following methods for additional information on how they collect and store data.
        methods = ['getEditions', 'getMetadata', 'to13', 'to10', 'fixChecksum', 'hyphen']"""

        self.isbn = isbn
        self.attributes = []  # TODO: Maintain this
        self.added_metadata = False
        self.status = None

        if len(isbn) == 10:
            self.isbn10 = isbn
            self.isbn13 = None
        if len(isbn) == 13:
            self.isbn13 = isbn
            self.isbn10 = None

        if len(isbn) in [10, 13]:
            self.attributes.extend(['isbn10', 'isbn13'])

    def _get_response(self, method):
        """A helper function for looking up the requested API methods and returning the raw data."""

        url = api_url.format(isbn=self.isbn, method=method)  # Generate URL for API
        urlf = urlopen(url)  # Retrieve URL as a JSON file object
        response = json.load(urlf)  # Parse
        urlf.close()

        status = response['stat']
        self.status = status
        if status == 'ok':
            return response
        else:
            raise QueryError("Could not find '%s'\n\tReason: %s" % (self.isbn, status))  # TODO: Add a fall back on the to13 or to10 methods of the API

    def getEditions(self, desired_attributes=maximal_parameters):  # TODO: Make a test for this one? There is a lot of output.
        """Gets info of all available editions of self.isbn.

Args:
    desired_parameters (list of strings):  The parameters that you would like to search for.
        Pre-made minimal_parameters and maximal_parameters (default) are in the isbn.py script.
        minimal_parameters = ['title', 'author', 'publisher', 'year', 'city']
        maximal_parameters = ['city', 'ed', 'form', 'AA', 'lang', 'lccn', 'oclcnum', 'originalLang', 'publisher', 'title', 'url', 'year']

Sets:
    Creates self.editions - A list of dictionaries.
        The keys to each dictionary are the desired_attributes.
        Values default to None if not found online.

Example:
    >>> book = Book('0446360260')  # ISBN-10
    >>> book.getEditions(['title', 'author'])
    >>> hasattr(book, 'editions')
    True
    >>> type(book.editions)
    <type 'list'>
    >>> len(book.editions)
    11

    """

        response = self._get_response('getEditions')
        self.editions = []
        self.attributes.append('editions')  # A list of dictionaries holding information about each edition.
        for item in response['list']:
            edition = {}
            for attribute in desired_attributes:
                try:
                    value = item[attribute]
                except KeyError:  # Will happen if a desired attribute is not present in an edition entry.
                    value = None
                edition[attribute] = value
            self.editions.append(edition)

    def getMetadata(self, desired_attributes=maximal_parameters):
        """Gets metadata about self.isbn.

Args:
    desired_parameters (list of strings):  The parameters that you would like to search for.
        Pre-made minimal_parameters and maximal_parameters (default) are in the isbn.py script.
        minimal_parameters = ['title', 'author', 'publisher', 'year', 'city']
        maximal_parameters = ['city', 'ed', 'form', 'AA', 'lang', 'lccn', 'oclcnum', 'originalLang', 'publisher', 'title', 'url', 'year']

Sets:
    Creates self.editions (A list of dictionaries.)
        The keys to each dictionary are the desired_attributes.
        Values default to None if not found online.

Example:
    >>> book = Book('9780821571095')  # ISBN-13
    >>> book.getMetadata()  # desired_parameters defaults to all of the possible values.
    >>> for attr in book.attributes:
    >>>     print attr + ': ', getattr(book, attr)
    isbn10:  None
    isbn13:  9780821571095
    city:  New York, N.Y.
    ed:  New ed.
    form:  ['BA']
    lang:  eng
    oclcnum:  ['62148511', '699975425']
    publisher:  Sadlier-Oxford
    title:  Vocabulary workshop.
    url:  ['http://www.worldcat.org/oclc/62148511?referer=xid']
    year:  2005
"""

        acquired_attributes = []
        response = self._get_response('getMetadata')
        if not response:
            return False# Break here if invalid.
        for data in response['list']:
            for name in desired_attributes:
                if name in data:
                    value = data[name]
                    setattr(self, name, value)
                    acquired_attributes.append(name)

        if not self.added_metadata:
            self.attributes.extend(acquired_attributes)
            self.added_metadata = True

    def to13(self):
        """Converts an ISBN-10 number to ISBN-13.

If the number is already ISBN-13, then nothing happens.
The result gets stored in self.isbn13"""

        if not self.isbn13:
            isbns = []
            response = self._get_response('to13')
            if not response:
                return  # Break here if invalid.
            for item in response['list']:
                for isbn in item['isbn']:
                    isbns.append(isbn)  # TODO: Overkill? Maybe I should just get the first result instead of going over every single result.
            #print "isbn10: %s --> isbn13: %s" % (self.isbn, isbns[0])
            self.isbn13 = isbns[0]
            return isbns[0]  # TODO: Return the whole list?

    def to10(self):
        """Converts an ISBN-13 number to ISBN-10.

If the number is already ISBN-10, then nothing happens.
The result gets stored in self.isbn10"""

        if not self.isbn10:
            isbns = []
            response = self._get_response('to10')
            if not response:
                return  # Break here if invalid.
            for item in response['list']:
                for isbn in item['isbn']:
                    isbns.append(isbn)  # TODO: Overkill? Maybe I should just get the first result instead of going over every single result.
            #print "isbn13: %s --> isbn10: %s" % (self.isbn, isbns[0])
            self.isbn10 = isbns[0]
            return isbns[0]  # TODO: Return the whole list?

    def fixChecksum(self):
        """Fixes the last digit of an incorrect ISBN-13 number.
        
The last digit of a ISBN-13 value is calculated with the ISBN number up until that last number.
See http://www.isbn-13.info/ for more information on how this is done.

This function will take an ISBN-13 number with an incorrect final digit, and correct it.

Sets (resets):
    self.isbn (the corrected ISBN-13 number)

Example:

>>> book = Book('9780821571097')
>>> try:
...     book.getMetadata()
... except QueryError, error:
...     print(error)
...
Could not find '9780821571097'
    Reason: invalidId
>>> book.fixChecksum()
>>> try:
...     book.getMetadata()
... except QueryError, error:
...     print(error)
...
>>> book.title
'Vocabulary workshop.'
"""
        response = self._get_response('fixChecksum')
        for item in response['list']:
            fixedChecksum = item['isbn']
            if fixedChecksum:
                self.isbn = fixedChecksum[0]
            self.attributes.append('fixedChecksum')
            return fixedChecksum

    def hyphen(self):
        response = self._get_response('hyphen')
        for item in response['list']:
            hyphenated = item['isbn']
            if hyphenated:  # To prevent an IndexError in the case of an empty list.
                self.hyphenated = hyphenated[0]
            self.attributes.append('hyphenated')
            return hyphenated
            break  # Is this necessary?

    def collect_all(self, attributes=maximal_parameters):
        self.getEditions(attributes)
        self.getMetadata(attributes)
        self.to10()
        self.to13()
        self.fixChecksum()
        self.hyphen()

    def __repr__(self):
        if self.isbn13:
            isbn = self.isbn13
            fmt = 'isbn-13'

        else:
            isbn = self.isbn10
            fmt = 'isbn-10'

        return "<Book(%s='%s')>" % (fmt, isbn)

if __name__ == '__main__':

    book = Book('9780821571097')
