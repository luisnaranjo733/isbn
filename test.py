import android


droid = android.Android()
code = droid.scanBarcode()

print code

"""
from biblio.webquery.xisbn import XisbnQuery
from biblio.webquery.errors import QueryError
from pprint import pprint
#TODO: Loop the main() function
#TODO: Add a way to break out of the loop
#TODO: Add suport for 'SCAN_RESULT_FORMAT': u'UPC_A' 10 digit ISBN on old books
DEBUG = False  # Possible bug on phone when True
TTS = True
ASK = False

def request(isnb, attrs=['title', 'year', 'authors']):
    book = {}
    book['isbn'] = isbn
    query = XisbnQuery()
    try:
        results = query.query_bibdata_by_isbn(isbn)
    except QueryError, error:
        print("QUERY ERROR")
        print(error)

    result = results[0]

    for attr in attrs:
        value = getattr(result, attr)

        line = "%s: %s" % (attr.upper(), value)
        #print(line)
        book[attr] = value

    return book



def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10

def check_digit_10(isbn):
    assert len(isbn) == 9
    sum = 0
    for i in range(len(isbn)):
        c = int(isbn[i])
        w = i + 1
        sum += w * c
    r = sum % 11
    if r == 10: return 'X'
    else: return str(r)

def check_digit_13(isbn):
    assert len(isbn) == 12
    sum = 0
    for i in range(len(isbn)):
        c = int(isbn[i])
        if i % 2: w = 3
        else: w = 1
        sum += w * c
    r = 10 - (sum % 10)
    if r == 10: return '0'
    else: return str(r)

def convert_10_to_13(isbn):
    assert len(isbn) == 10
    prefix = '978' + isbn[:-1]
    check = check_digit_13(prefix)
    return prefix + check

tests = [
    ('1566199093', '9781566199094'),
    ('0312538618', '9780312538613'),
    ('0439784549', '9780439784542'),
]

for isbn10, isbn13 in tests:
    assert isbn13 == convert_10_to_13(isbn10)

droid = android.Android()

code = droid.scanBarcode()
isbn = code.result['extras']['SCAN_RESULT'][1:-1]

isbn13 = convert_10_to_13(isbn)
print(isbn13)

print(request(isbn13))"""

