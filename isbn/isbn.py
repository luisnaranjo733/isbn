try:
    import simplejson as json
except ImportError:
    import json
from urllib import urlopen
from pprint import pprint

methods = ['getMetadata', 'to13', 'to10', 'fixChecksum', 'hyphen']
supported_methods = methods[:3]

api_url = 'http://xisbn.worldcat.org/webservices/xid/isbn/{isbn}?method={method}&format=json&fl=*'  # formats available: (python,csv,xml)
#  TODO: Add &ai={affiliate_ID}

global maximal_attributes
minimal_attributes = ['title', 'author', 'publisher', 'year', 'city']
maximal_attributes = ['city', 'ed', 'form', 'AA', 'lang', 'lccn', 'oclcnum', 'originalLang', 'publisher', 'title', 'url', 'year']


class Book(object):
    def __init__(self, isbn):
        """Takes url and method as input, returns API object.

        Attributes are created dynamically, depending on their availability."""
        self.isbn = isbn
        self.attributes = []  # TODO: Maintain this
        self.added_metadata = False

        if len(isbn) == 10:
            self.isbn10 = isbn
            self.isbn13 = None
        if len(isbn) == 13:
            self.isbn13 = isbn
            self.isbn10 = None

        if len(isbn) in [10, 13]:
            self.attributes.extend(['isbn10', 'isbn13'])

    def get_response(self, method):
        url = api_url.format(isbn=self.isbn, method=method)  # Generate URL for API
        urlf = urlopen(url)  # Retrieve URL as a JSON file object
        response = json.load(urlf)  # Parse
        urlf.close()

        status = response['stat']
        if status == 'ok':
            return response
        else:
            return None
            raise Exception("Could not find '%s'\n\tReason: %s" % (self.isbn, status))  # TODO: Add a fall back on the to13 or to10 methods of the API

    def getEditions(self, desired_attributes=maximal_attributes):
        response = self.get_response('getEditions')
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

    def getMetadata(self, desired_attributes=maximal_attributes):
        """Returns a list of the newly attributes."""

        acquired_attributes = []
        response = self.get_response('getMetadata')
        if not response:
            return  # Break here if invalid.
        for data in response['list']:
            for name in desired_attributes:
                if name in data:
                    value = data[name]
                    setattr(self, name, value)
                    acquired_attributes.append(name)

        if not self.added_metadata:
            self.attributes.extend(acquired_attributes)
            self.added_metadata = True
        return acquired_attributes

    def to13(self):
        isbns = []
        response = self.get_response('to13')
        if not response:
            return  # Break here if invalid.
        for item in response['list']:
            for isbn in item['isbn']:
                isbns.append(isbn)  # TODO: Overkill? Maybe I should just get the first result instead of going over every single result.
        #print "isbn10: %s --> isbn13: %s" % (self.isbn, isbns[0])
        self.isbn13 = isbns[0]
        return isbns[0]  # TODO: Return the whole list?

    def to10(self):
        isbns = []
        response = self.get_response('to10')
        if not response:
            return  # Break here if invalid.
        for item in response['list']:
            for isbn in item['isbn']:
                isbns.append(isbn)  # TODO: Overkill? Maybe I should just get the first result instead of going over every single result.
        #print "isbn13: %s --> isbn10: %s" % (self.isbn, isbns[0])
        self.isbn10 = isbns[0]
        return isbns[0]  # TODO: Return the whole list?

    def fixChecksum(self):
        response = self.get_response('fixChecksum')
        for item in response['list']:
            fixedChecksum = item['isbn']
            if fixedChecksum:
                self.fixedChecksum = fixedChecksum[0]
            self.attributes.append('fixedChecksum')
            return fixedChecksum

    def hyphen(self):
        response = self.get_response('hyphen')
        for item in response['list']:
            hyphenated = item['isbn']
            if hyphenated:  # To prevent an IndexError in the case of an empty list.
                self.hyphenated = hyphenated[0]
            self.attributes.append('hyphenated')
            return hyphenated
            break  # Is this necessary?

    def collect_all(self, attributes=maximal_attributes):
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

    book = Book('0446360260')
    book.collect_all()
    pprint(book.editions)
