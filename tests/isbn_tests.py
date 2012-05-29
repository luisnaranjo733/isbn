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
        'hyphenated': '978-0-312-53861-3',

    },
    '9780451524935': {
        'isbn10': '0451524934',  # These should all be expected attributes of the new instance
        'isbn13': '9780451524935',
        'title': "1984 : a novel",
        'author': "by George Orwell ; with an afterword by Erich Fromm.",
        'publisher': "Signet Classic",
        'year': '1961',
        'city': 'New York, N.Y.',
        'hyphenated': '978-0-451-52493-5',

    },
    '9780439784542': {
        'isbn10': '0439784549',  # These should all be expected attributes of the new instance
        'isbn13': '9780439784542',
        'title': "Harry Potter and the half-blood prince",
        #'author': 'J.K. Rowling ; illustrations by Mary GrandPr\xc3.',  # Ommitting this one because it has a non-ASCII char in it
        'publisher': "Scholastic Inc.",
        'year': '2005',
        'city': 'New York, NY',
        'hyphenated': '978-0-439-78454-2',

    },
    '0446360260': {
        'isbn10': '0446360260',  # These should all be expected attributes of the new instance
        'isbn13': '9780446360265',
        'title': "Webster's new world dictionary",
        'author': 'Victoria Neufeldt, editor in chief ; Andrew N. Sparks, project editor.',
        'publisher': 'Warner Books',
        'year': '1990',
        'city': 'New York (N.Y.)',
        'hyphenated': '0-446-36026-0',

    },
}


def test_api():
    results = []
    for isbn in tests:
        info = tests[isbn]
        print("Testing: '%s'" % (info['title']))
        book = Book(isbn)
        assert book.isbn == isbn

        book.collect_all()  # Gather all possible information

        for attribute in info:
            result = getattr(book, attribute) == info[attribute]
            print("\tIs %s correct?: %r" % (attribute, result))
            assert result
            results.append(result)

    if all(results):
        print("All of the tests have passed.")

    if not all(results):
        print ("Not all of the tests have passed.")


if __name__ == '__main__':
    import nose
    #result = nose.run()
    test_api()
