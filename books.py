from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [
    {"title" : "title one", "author" : "author one", "category" : "science"},
    {"title" : "title two", "author" : "author two", "category" : "science"},
    {"title" : "title three", "author" : "author three", "category" : "history"},
    {"title" : "title four", "author" : "author four", "category" : "math"},
    {"title" : "title five", "author" : "author five", "category" : "math"},
    {"title" : "title six", "author" : "author two", "category" : "math"},
]

@app.get("/api-endpoint")
async def first_api():
    return {"message": "Hello from the first API!"}

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/book_title")
async def read_book(book_title: str):
    for book in BOOKS:
        if book["title"].casefold() == book_title.casefold():
            return book

@app.get("/books/")
async def read_books_by_category(category: str):
    books_in_category = []
    for book in BOOKS:
        if book["category"].casefold() == category.casefold():
            books_in_category.append(book)
    return books_in_category

@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str, category: str):
    books_in_category = []
    for book in BOOKS:
        if book["author"].casefold() == book_author.casefold() and book["category"].casefold() == category.casefold():
            books_in_category.append(book)
    return books_in_category

@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)

@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i]["title"].casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book
            return {"message": "Book updated successfully"}

@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i]["title"].casefold() == book_title.casefold():
            print({"message": f"Book {BOOKS[i]['title']} deleted successfully"})
            del BOOKS[i]

@app.get("/books/search/{author}")
async def search_books(author: str):
    books_by_author = []
    for book in BOOKS:
        if book["author"].casefold() == author.casefold():
            books_by_author.append(book)
    return books_by_author
            