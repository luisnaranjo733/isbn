try:
    import simplejson as json
except ImportError:
    import json
from urllib import urlopen

methods = ['getMetadata', 'to13', 'to10', 'fixChecksum', 'getEditions']
supported_methods = methods[:3]

api_url = 'http://xisbn.worldcat.org/webservices/xid/isbn/{isbn}?method={method}&format=json&fl=*'  # formats available: (python,csv,xml)
#  TODO: Add &ai={affiliate_ID}

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

    def get_response(self, method):
        url = api_url.format(isbn=self.isbn, method=method)  # Generate URL for api
        urlf = urlopen(url)  # Retrieve url as a JSON file object
        response = json.load(urlf)  # Parse
        urlf.close()

        status = response['stat']
        if status == 'ok':
            return response
        else:
            raise Exception("Could not find '%s'\n\tReason: %s" % (self.isbn, status))  # TODO: Add a fallback on the to13 or to10 methods of the API


    def getMetadata(self, desired_attributes=['title', 'author', 'publisher', 'year', 'city']):
        """Returns a list of the newly attributes."""

        acquired_attributes = []
        response = self.get_response('getMetadata')
        for data in response['list']:
            for name in desired_attributes:
                if data.has_key(name):
                    value = data[name]
                    setattr(self, name, value)  
                    acquired_attributes.append(name)

        if not self.added_metadata:
            self.attributes.extend(acquired_attributes)
            self.added_metadata = True
        return acquired_attributes

        print "Parsing metadata...."

    def to13(self):
        isbns = []
        response = self.get_response('to13')
        for item in response['list']:
            for isbn in item['isbn']: isbns.append(isbn)  # TODO: Overkill? Maybe I should just get the first result instead of going over every single result.
        print "isbn10: %s --> isbn13: %s" % (self.isbn, isbns[0])
        self.isbn13 = isbns[0]
        return isbns


    def to10(self):
        isbns = []
        response = self.get_response('to13')
        for item in response['list']:
            for isbn in item['isbn']: isbns.append(isbn)  # TODO: Overkill? Maybe I should just get the first result instead of going over every single result.
        print "isbn13: %s --> isbn10: %s" % (self.isbn, isbns[0])
        self.isbn10 = isbns[0]
        return isbns


    def __repr__(self):
        return "<Book(isbn='%s')>" % self.isbn

api = Book(isbn='0312538618')
#api.getMetadata()
#api.to13()
#print "ISBN-13 = %s" % api.isbn13
#print "ISBN-10 = %s" % api.isbn10
