'''
1. Capture ISBN
2. Possibly convert
3. Lookup metadata with API
4. Confirm data
5. Write data to disk
6. Repeat the process until the exit barcode is scanned.
'''

import sys
import os
from datetime import datetime
import android
from lookup import Book, minimal_parameters, QueryError

droid = android.Android()

catalog_path = '/sdcard/sl4a/scripts/isbn/books.txt' # desired path to catalogue file
if sys.platform == 'linux2':  # For development
    catalog_path = os.path.join(os.environ['PWD'], 'books.txt')


def prettify(data):
    '''Takes a dictionary of data and returns it as a pretty string.'''
    pretty = ''
    for param in data:
        pretty += '%s: %s\n' % (param.upper(), data[param])
    return pretty

def capture():
    '''Scans a barcode in droid and returns an ISBN string'''
    result = droid.scanBarcode().result['extras']
    return result['SCAN_RESULT'], result['SCAN_RESULT_FORMAT']


def convert(raw_isbn, fmt):
    '''Converts any uncompatible barcode formats'''
    print raw_isbn, fmt
    return raw_isbn


def lookup(isbn):
    '''Takes an isbn number and returns a dictionary of book metadata.
    
    minimal parameters is a list of strings. These strings are the attributes
    that we are querying for. The Book class stores them as "book.attribute".
    For example, "book.title".'''
    book = Book(isbn)
    book.getMetadata(minimal_parameters) # API request made here
    data = {}
    for param in minimal_parameters + ['isbn']:
        if hasattr(book, param):
            data[param] = getattr(book, param)
    return data
    

def confirm(data):
    body = prettify(data)
    droid.dialogCreateAlert(data['title'], body)
    droid.dialogSetPositiveButtonText('Confirm')
    droid.dialogSetNeutralButtonText('Cancel')
    droid.dialogShow()
    response = droid.dialogGetResponse().result
    if response['which'] == 'positive':
        return True
    else:
        return False

def write(data, failed=False, fmt=None):
    '''Handles writing data to disk.

    If only data is passed, a dictionary of information is expected.
    If data and failed, data is expected to be an isbn string.'''

    entry = 'ENTRY TIME: %s\n' % datetime.now().strftime('%c')

    if not failed:
        entry += prettify(data)
        droid.makeToast('Cataloged: %s' % data['title'])

    if failed:
        entry += 'UNKNOWN ISBN: %r\n' % data
        entry += 'FORMAT: %s\n' % fmt
        droid.makeToast('Logged %r code.' % isbn)

    entry += '=' * 72 + '\n'

    with open(catalog_path, 'a') as fh:
        fh.write(entry)



if __name__ == '__main__':

    while True:
        raw_isbn, fmt = capture() #1
        if raw_isbn == '000000000000':
            droid.makeToast('Bye Bye!')
            break
        isbn = convert(raw_isbn, fmt) #2
        try:
            data = lookup(isbn) #3
            data['fmt'] = fmt
        except QueryError, tb:
            droid.vibrate()
            droid.makeToast('ERROR: %s' % tb.reason)
            write(isbn, failed=True, fmt=fmt)
            continue

        if confirm(data): #4
            write(data) #5


