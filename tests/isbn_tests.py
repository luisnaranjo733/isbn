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
    '9780451524935' : {
        'isbn10': '0451524934',  # These should all be expected attributes of the new instance
        'isbn13': '9780451524935',
        'title': "1984 : a novel",
        'author': "by George Orwell ; with an afterword by Erich Fromm.",
        'publisher': "Signet Classic",
        'year': '1961',
        'city': 'New York, N.Y.',
    },
}


def test_all():
    for isbn in tests:
        info = tests[isbn]
        book = Book(isbn)
        assert book.isbn == isbn

        book.getMetadata()
        book.to10()
        book.to13()

        for attribute in info:
            assert getattr(book, attribute) == info[attribute]

test_all()
