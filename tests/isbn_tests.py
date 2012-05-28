from isbn.isbn import Book

def test_all():
    isbn = '0312538618'
    book = Book(isbn)
    assert book.isbn ==  isbn

test_all()
