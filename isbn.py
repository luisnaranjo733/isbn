import sys

import android
from biblio.webquery.xisbn import XisbnQuery
from biblio.webquery.errors import QueryError

#TODO: Loop the main() function
#TODO: Add a way to break out of the loop

DEBUG = False
TTS = True
ASK = False

def request(isnb, attrs=['title', 'year', 'authors']):
    book = {}
    book['isbn'] = isbn
    query = XisbnQuery()
    try:
        results = query.query_bibdata_by_isbn(isbn)
    except QueryError, error:
        print(error)

    result = results[0]

    for attr in attrs:
        value = getattr(result, attr)

        line = "%s: %s" % (attr.upper(), value)
        #print(line)
        book[attr] = value

    return book

def describe(book):
    for key in book:
        sep = 'is'
        value = book[key]
        if isinstance(value, list):
            value = ', '.join([a.family for a in value])
            if len(value) > 1:
                sep ='are'
        line = "%s: %s" % (key.upper(), value)
        yield line


def main(droid, TTS, ASK):
    global isbn

    if not DEBUG:
        code = droid.scanBarcode()
        isbn = code.result['extras']['SCAN_RESULT']
    if DEBUG:
        isbn = '9780451524935'

    info = request(isbn)

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

    path = '/sdcard/sl4a/scripts/isbn/books.txt'
    if sys.platform == 'linux2':  # For development
        path = '/home/luis/Dropbox/projects/android/isbn/books.txt'

    title = title

    buff = '| '

    entry = title + buff + ', '.join([a.family for a in info['authors']]) + buff + isbn + '\n'

    with open(path, 'a') as fhandle:
        #fhandle.write(unicode(title,"utf-8").encode("utf-8","ignore"))  
        fhandle.write(entry)

if __name__ == '__main__':
    droid = android.Android()
    main(droid, TTS, ASK)

sys.exit(0)
