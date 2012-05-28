import sys

import android

from biblio.webquery.xisbn import XisbnQuery
from biblio.webquery.errors import QueryError
from xmlrpclib import ServerProxy, Error
from pprint import pprint


#TODO: Loop the main() function
#TODO: Add a way to break out of the loop
#TODO: Add suport for 'SCAN_RESULT_FORMAT': u'UPC_A' 10 digit ISBN on old books

global rpc_key, path
rpc_key = 'ffffa702254fa9ace07a44cfb15847a015a985fd'

path = '/sdcard/sl4a/scripts/isbn/books.txt'
if sys.platform == 'linux2':  # For development
    path = '/home/luis/Dropbox/projects/android/src/books.txt'


DEBUG = True  # Possible bug on phone when True
TTS = True
ASK = False

def lookup_upc(upc):  # For looking up upc's (COSTS MONEY - 20 freebies a day)
    server = ServerProxy('http://www.upcdatabase.com/xmlrpc')
    params = {'rpc_key': rpc_key, 'upc': upc}
    response = server.lookup(params) # Dict - Keys: upc, ean, description, issuerCountry
    if response['status'] == 'success':
        book = {}
        book['isbn']  = upc
        book['title'] = response['description']
        book['upc'] = response['upc']
        book['ean'] = response['ean']
        book['authors'] = None
        return book
        


def request(isnb, attrs=['title', 'authors']):
    book = {}
    book['isbn'] = isbn
    query = XisbnQuery()
    try:
        results = query.query_bibdata_by_isbn(isbn)
    except QueryError, error:
        print("QUERY ERROR (EAN_13)")
        print("TRYING UPC_A")
        return lookup_upc(isnb)

    try:
        result = results[0]  # Get first result
    except IndexError:
        result = results

    for attr in attrs:
        value = getattr(result, attr)

        line = "%s: %s" % (attr.upper(), value)
        #print(line)
        book[attr] = value

    return book

def describe(book):  # Compatible
    for key in book:
        value = book[key]
        if isinstance(value, list):
            value = ', '.join([a.family for a in value])  # Turning family attribute list into a nice string

        line = "%s: %s" % (key.upper(), value)
        yield line


def main(droid, TTS, ASK):
    global isbn
    if not DEBUG:
        code = droid.scanBarcode()  # SCAN_RESULT_FORMAT
        isbn = code.result['extras']['SCAN_RESULT']
        if isbn == "000000000000":
            droid.makeToast("Exiting loop.\nBye Bye!")
            return False
        fmt = code.result['extras']['SCAN_RESULT_FORMAT']
    if DEBUG:
        isbn = '9780451524935' # len13
        fmt = 'EAN_13'
        isbn = '070993004507'  # len12
        fmt = 'EAN_13'#'UPC_A'

    if fmt == 'EAN_13':
        info = request(isbn)
    if fmt == 'UPC_A':
        info = lookup_upc(upc=isbn)

    output = [a for a in describe(info)]
    title = info['title']
    title_msg = "Found: '%s'" % title
    message = '\n'.join(output)

    if TTS is not None and ASK:
        droid.dialogCreateAlert(title_msg, message)
        droid.dialogSetPositiveButtonText("Speak")
        droid.dialogSetNeutralButtonText("Don't speak")
        droid.dialogShow()
        response=droid.dialogGetResponse().result
        TTS = None

        if response['which'] == 'positive':
            TTS = True

        if response['which'] == 'negative':
            TTS = False

    if not ASK:
        droid.makeToast(message)

    droid.dialogDismiss()
    if TTS:
        droid.ttsSpeak(title)

    while droid.ttsIsSpeaking().result:
        pass  # Prevents the script from exiting before TTS is done.

    title = title

    buff = '| '

    if fmt == 'EAN_13':
        entry = title + buff + ', '.join([a.family for a in info['authors']]) + buff + isbn + '\n'
    if fmt == 'UPC_A':
        entry = title + buff + str(info['authors']) + buff + isbn + '\n'

    with open(path, 'a') as fhandle:
        #fhandle.write(unicode(title,"utf-8").encode("utf-8","ignore"))  
        fhandle.write(entry)
        print("Added: " + entry)

    return True
if __name__ == '__main__':
    droid = android.Android()
    while main(droid, TTS, ASK):
        if DEBUG: break

    sys.exit(0)
