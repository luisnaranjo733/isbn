from isbn import Book

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
    '9780439784542' : {
        'isbn10': '0439784549',  # These should all be expected attributes of the new instance
        'isbn13': '9780439784542',
        'title': "Harry Potter and the half-blood prince",
        #'author': 'J.K. Rowling ; illustrations by Mary GrandPr\xc3.',  # Ommitting this one because it has a non-ASCII char in it
        'publisher': "Scholastic Inc.",
        'year': '2005',
        'city': 'New York, NY',

    },
}


def test_api():
    for isbn in tests:
        info = tests[isbn]
        book = Book(isbn)
        assert book.isbn == isbn

        book.getMetadata()
        book.to10()
        book.to13()

        for attribute in info:
            assert getattr(book, attribute) == info[attribute]

test_api()
