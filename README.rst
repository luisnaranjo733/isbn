ISBN
****

A Python isbn request library using the http://xisbn.worldcat.org/xisbnadmin/doc/api.htm API.

ISBN provides a Book class, which has all of the methods described on the xisbn.worldcat API, implemented in Python.

ISBN supports both ISBN-10 and ISBN-13 numbers at the moment.

**ISBN is under active development**

Basic Usage
***********

>>> from isbn import Book
>>> book = Book('9780821571097')
>>> book.getMetadata()
>>> book.title
'Vocabulary workshop.'

>>> book = Book('9780821571095')  # ISBN-13
>>> book.getMetadata()  # desired_parameters defaults to all of the possible values.
>>> for attr in book.attributes:  # A list of attributes that is created dependinging the available data.
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