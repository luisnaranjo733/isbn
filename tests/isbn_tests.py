import sys
sys.path.append('/home/luis/Dropbox/projects/android/isbn')
from isbn.isbn import Book

tests = {
    '9780312538613': {  # ISBN at __init__
        'isbn10': '0312538618',  # These should all be expected attributes of the new instance
        'isbn13': '9780312538613',
        'title': "Everything's an argument : with readings",
        'author': "Andrea A. Lunsford, John J. Ruszkiewicz, Keith Walters.",
        'publisher': "Bedford/St. Martins",
        'year': '2010',
        'city': 'Boston',

    },
}

def test_book(isbn, info):
    book = Book(isbn)
    assert book.isbn == isbn

    book.getMetadata()
    book.to10()
    book.to13()

    for attribute in info:
        assert getattr(book, attribute) == info[attribute]


def test_all():
    for isbn in tests:
        info = tests[isbn]
        test_book(isbn, info)
test_all()
