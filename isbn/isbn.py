try:
    import simplejson as json
except ImportError:
    import json
from urllib import urlopen
from pprint import pprint


methods = ['getMetadata', 'to13', 'to10', 'fixChecksum', 'getEditions']
supported_methods = methods[:3]

api_url = 'http://xisbn.worldcat.org/webservices/xid/isbn/{isbn}?method={method}&format={fmt}&fl=*'  # formats available: (python,csv,xml)


class Book(object):
    def __init__(self, isbn, method, fmt='json'):
        """Takes url and method as input, returns API object.

        Attributes are created dynamically, depending on their availability."""
        self.isbn = isbn
        self.method = method
        self.attributes = []

        if len(isbn) == 10:
            self.isbn10 = isbn
            self.isbn13 = None
        if len(isbn) == 13:
            self.isbn13 = isbn
            self.isbn10 = None

        url = api_url.format(isbn=isbn, method=method, fmt=fmt)  # Generate URL for api
        urlf = urlopen(url)  # Retrieve url as a JSON file object
        response = json.load(urlf)  # Parse
        urlf.close()

        status = response['stat']
        if status == 'ok':
            self.api = response
        else:
            self.api = None
            raise Exception("Could not find '%s'\n\tReason: %s" % (isbn, status))  # TODO: Add a fallback on the to13 or to10 methods of the API

        execute_method = getattr(self, method)
        execute_method()

    def getMetadata(self):
        desired_attributes = ['title', 'author', 'publisher', 'year', 'city']
        for data in self.api['list']:
            for name in desired_attributes:
                if data.has_key(name):
                    value = data[name]
                    setattr(self, name, value)  
                    self.attributes.append(name)

        print "Parsing metadata...."

    def to13(self):
        isbns = []
        for item in self.api['list']:
            for isbn in item['isbn']: isbns.append(isbn)  # TODO: Overkill? Maybe I should just get the first result instead of going over every single result.
        print "isbn10: %s --> isbn13: %s" % (self.isbn, isbns[0])
        self.isbn13 = isbns[0]
        return isbns


    def to10(self):
        isbns = []
        for item in self.api['list']:
            for isbn in item['isbn']: isbns.append(isbn)  # TODO: Overkill? Maybe I should just get the first result instead of going over every single result.
        print "isbn13: %s --> isbn10: %s" % (self.isbn, isbns[0])
        self.isbn10 = isbns[0]
        return isbns


    def __repr__(self):
        return "<Book(isbn='%s', method='%s')>" % (self.isbn, self.method)

api = Book(isbn='0312538618', method='getMetadata')
#api.getMetadata()
api.to13()
print "ISBN-13 = %s" % api.isbn13
print "ISBN-10 = %s" % api.isbn10
